# -*- coding: utf-8 -*-
from DateTime import DateTime
from datetime import timedelta
from lxml import etree
from plone.dexterity.content import Item
from plone.supermodel import model
from unikold.connector import _
from unikold.connector.interfaces import IUniKoLdQuery
from zope import schema
from zope.interface import implementer

import base64
import urllib2


class IXMLQuery(model.Schema):

    url = schema.TextLine(
        title=_(u'URL'),
        required=True
    )

    query_params = schema.List(
        title=_(u'Query parameters'),
        value_type=schema.TextLine(
            title=_(u'Parameter')
        ),
        required=False
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

    basic_auth_username = schema.TextLine(
        title=_(u'Username for basic access authentication'),
        required=False
    )

    basic_auth_password = schema.Password(
        title=_(u'Password for basic access authentication'),
        required=False
    )

    exclude_from_auto_update = schema.Bool(
        title=_(u'Exclude from automated updates'),
        required=False,
        default=False
    )


@implementer(IXMLQuery, IUniKoLdQuery)
class XMLQuery(Item):

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
            self.raw_response = str(data)
            self.raw_error = False
            self.setModificationDate(DateTime())
            return data
        else:
            self.raw_error = str(err)
        return False

    def getRawResponse(self):
        data = self.raw_response
        try:
            queryStr = self.buildQueryStr()

            if self.basic_auth_username is not None and \
               self.basic_auth_password is not None:
                # if credentials for basic authentication are set,
                # include necessary headers to perform authentication
                username = self.basic_auth_username
                password = self.basic_auth_password
                request = urllib2.Request(self.url + queryStr)
                base64string = base64.b64encode('{0}:{1}'.format(username, password))
                request.add_header('Authorization', 'Basic {0}'.format(base64string))

                opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
                data = opener.open(request).read()
                err = False
            else:
                # otherwise perform simple request
                response = urllib2.urlopen(self.url + queryStr)
                data = response.read()
                err = False

        except urllib2.URLError as e:
            err = e.reason
        except ValueError as e:
            err = e
        return (data, err)

    def getXMLResponse(self):
        if hasattr(self, 'raw_response'):
            try:
                tree = etree.fromstring(self.raw_response)
            except (etree.XMLSyntaxError, ValueError):
                tree = etree.Element('xml-syntax-error')
            return tree
        return etree.Element('empty')

    def buildQueryStr(self):
        if self.query_params is None:
            return ''

        queryParts = []
        for param in self.query_params:
            parts = param.split('=')
            if len(parts) != 2:
                # query parameters have to be formatted like: `key=value`
                continue
            queryParts.append(
                '{0}={1}'.format(urllib2.quote(parts[0]), urllib2.quote(parts[1]))
            )

        if len(queryParts) > 0:
            return '?' + '&'.join(queryParts)
        return ''
