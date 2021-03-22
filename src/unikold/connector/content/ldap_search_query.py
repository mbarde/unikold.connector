# -*- coding: utf-8 -*-
from datetime import timedelta
from DateTime import DateTime
from plone import api
from plone.dexterity.content import Item
from plone.supermodel import model
from unikold.connector import _
from unikold.connector.interfaces import IUniKoLdQuery
from zope import schema
from zope.interface import implementer

import ldap
import pickle


class ILDAPSearchQuery(model.Schema):

    address = schema.TextLine(
        title=_(u'LDAP server address'),
        required=False,
    )

    port = schema.Int(
        title=_(u'LDAP server port'),
        required=False,
    )

    username = schema.TextLine(
        title=_(u'Username'),
        required=False,
    )

    password = schema.Password(
        title=_(u'Password'),
        required=False,
    )

    base_dn = schema.TextLine(
        title=_(u'Base DN'),
        required=False,
    )

    filter = schema.TextLine(
        title=_(u'Filter'),
        required=True,
    )

    raw_response = schema.Text(
        title=_(u'Raw Response'),
        required=False,
    )

    raw_error = schema.Text(
        title=_(u'Raw Error'),
        required=False,
    )

    lifetime = schema.Timedelta(
        title=_(u'Lifetime'),
        required=True,
        default=timedelta(hours=48),
    )

    exclude_from_auto_update = schema.Bool(
        title=_(u'Exclude from automated updates'),
        required=False,
        default=False,
    )


@implementer(ILDAPSearchQuery, IUniKoLdQuery)
class LDAPSearchQuery(Item):

    def getData(self, forceUpdate=False):
        # update data if there has not been a response yet ...
        if forceUpdate or self.raw_response is None:
            self.updateData()
        else:
            # ... or if lifetime of last update expired
            now = DateTime().asdatetime()
            modified = self.modified().asdatetime()
            if now > modified + self.lifetime:
                self.updateData()

        res = getattr(self, 'raw_response', None)
        if res is None:
            res = ''
        return res

    def updateData(self):
        (data, err) = self.getRawResponse()
        if err is False:
            self.raw_response = pickle.dumps(data)
            self.raw_error = False
            self.setModificationDate(DateTime())
            return data
        else:
            self.raw_error = str(err)
        return False

    def getRawResponse(self):
        data = self.raw_response
        err = False

        ldapClient = False
        try:
            address = self.getOptionalAttr('address')
            port = self.getOptionalAttr('port')
            username = self.getOptionalAttr('username')
            password = self.getOptionalAttr('password')
            base_dn = self.getOptionalAttr('base_dn')

            # see http://www.grotan.com/ldap/python-ldap-samples.html
            ldapClient = ldap.initialize('{0}:{1}'.format(address, port))
            ldapClient.simple_bind_s(username, password)
            ldapClient.protocol_version = ldap.VERSION3
            searchScope = ldap.SCOPE_SUBTREE

            ldap_result_id = ldapClient.search(
                base_dn, searchScope, self.filter, None)
            result_type, result_data = ldapClient.result(ldap_result_id, 0)
            ldapClient.unbind_s()

            data = result_data
        except Exception as e:  # noqa: B902
            err = str(e)
        finally:
            try:
                if ldapClient is not False:
                    ldapClient.unbind_s()
            except AttributeError:
                # client was not bound, so all o.k.
                pass

        return (data, err)

    def getResults(self):
        raw_response = getattr(self, 'raw_response', None)
        if raw_response is not None:
            try:
                return pickle.loads(self.raw_response)
            except Exception as e:  # noqa: B902
                return [(u'pickle loads error', str(e))]
        return []

    def getResultsWithoutDNs(self):
        results = []
        resultsWithDNs = self.getResults()
        for (dn, result) in resultsWithDNs:
            results.append(result)
        return results

    # returns value of attribute of self
    # if self does not has this attribute defined,
    # return default set in controlpanel
    def getOptionalAttr(self, attrName):
        if attrName not in ['address', 'port', 'username', 'password', 'base_dn']:
            return None

        val = getattr(self, attrName, None)
        if val is not None:
            if isinstance(val, str):
                if len(val) > 0:
                    return val
            else:
                return val

        regDefaultStr = 'unikold_connector_ldap.ldap_default_{0}'.format(attrName)
        return api.portal.get_registry_record(regDefaultStr)
