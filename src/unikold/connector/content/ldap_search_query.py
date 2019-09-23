# -*- coding: utf-8 -*-
from DateTime import DateTime
from datetime import timedelta
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
        required=True
    )

    port = schema.Int(
        title=_(u'LDAP server port'),
        required=True
    )

    username = schema.TextLine(
        title=_(u'Username'),
        required=True
    )

    password = schema.Password(
        title=_(u'Password'),
        required=True
    )

    base_dn = schema.TextLine(
        title=_(u'Base DN'),
        required=True
    )

    filter = schema.TextLine(
        title=_(u'Filter'),
        required=True
    )

    raw_response = schema.Text(
        title=_(u'Raw Response'),
        required=False
    )

    raw_error = schema.Text(
        title=_(u'Raw Error'),
        required=False
    )

    lifetime = schema.Timedelta(
        title=_(u'Lifetime'),
        required=True,
        default=timedelta(hours=48)
    )

    exclude_from_auto_update = schema.Bool(
        title=_(u'Exclude from automated updates'),
        required=False,
        default=False
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

        try:
            ''' see http://www.grotan.com/ldap/python-ldap-samples.html '''
            ldapClient = ldap.initialize('{0}:{1}'.format(self.address, self.port))
            ldapClient.simple_bind_s(self.username, self.password)
            ldapClient.protocol_version = ldap.VERSION3
            searchScope = ldap.SCOPE_SUBTREE

            ldap_result_id = ldapClient.search(
                self.base_dn, searchScope, self.filter, None)
            result_type, result_data = ldapClient.result(ldap_result_id, 0)
            ldapClient.unbind_s()

            data = result_data
        except Exception, e:
            err = str(e)
        finally:
            try:
                ldapClient.unbind_s()
            except AttributeError:
                # client was not bound, so all o.k.
                pass

        return (data, err)

    def getResults(self):
        raw_response = getattr(self, 'raw_response', None)
        if raw_response is not None:
            return pickle.loads(self.raw_response)
        return []

    def getResultsWithoutDNs(self):
        results = []
        resultsWithDNs = self.getResults()
        for (dn, result) in resultsWithDNs:
            results.append(result)
        return results
