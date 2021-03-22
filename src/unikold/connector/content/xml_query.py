# -*- coding: utf-8 -*-
from datetime import timedelta
from DateTime import DateTime
from lxml import etree
from plone.dexterity.content import Item
from plone.supermodel import model
from unikold.connector import _
from unikold.connector.interfaces import IUniKoLdQuery
from unikold.connector.utils_sentry import sentry_message
from zope import schema
from zope.interface import implementer

import base64
import urllib.error
import urllib.parse
import urllib.request


class IXMLQuery(model.Schema):

    url = schema.TextLine(
        title=_(u'URL'),
        required=True,
    )

    query_params = schema.List(
        title=_(u'Query parameters'),
        value_type=schema.TextLine(
            title=_(u'Parameter'),
        ),
        required=False,
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

    basic_auth_username = schema.TextLine(
        title=_(u'Username for basic access authentication'),
        required=False,
    )

    basic_auth_password = schema.Password(
        title=_(u'Password for basic access authentication'),
        required=False,
    )

    exclude_from_auto_update = schema.Bool(
        title=_(u'Exclude from automated updates'),
        required=False,
        default=False,
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
            self.raw_response = data
            self.raw_error = False
            self.setModificationDate(DateTime())
            return data
        else:
            self.raw_error = str(err)
            sentry_message('Error in XML response of {0}: {1}'
                           .format(self.absolute_url(), self.raw_error))
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
                request = urllib.request.Request(self.url + queryStr)
                base64string = base64.b64encode(
                    '{0}:{1}'.format(username, password).encode('ascii'),
                )
                request.add_header(
                    'Authorization',
                    'Basic {0}'.format(base64string.decode('ascii')),
                )

                opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
                data = opener.open(request).read()
                err = False
            else:
                # otherwise perform simple request
                response = urllib.request.urlopen(self.url + queryStr)
                data = response.read()
                err = False

        except urllib.error.URLError as e:
            err = e.reason
        except ValueError as e:
            err = e
        return (data, err)

    def getXMLResponse(self):
        response = getattr(self, 'raw_response', None)
        if response is not None:
            try:
                if not isinstance(response, bytes):
                    response = response.encode()
                tree = etree.fromstring(response)
            except (etree.XMLSyntaxError, ValueError):
                tree = etree.Element('xml-syntax-error')
                sentry_message('XML syntax error parsing raw_response of {0}'
                               .format(self.absolute_url()))
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
                '{0}={1}'.format(urllib.parse.quote(parts[0]), urllib.parse.quote(parts[1])),
            )

        if len(queryParts) > 0:
            return '?' + '&'.join(queryParts)
        return ''
