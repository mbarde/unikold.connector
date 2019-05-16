# -*- coding: utf-8 -*-
from DateTime import DateTime
from datetime import timedelta
from lxml import etree
from plone.dexterity.content import Item
from plone.supermodel import model
from unikold.connector import _
from zope import schema
from zope.interface import implementer

import urllib2


class IXMLQuery(model.Schema):

    url = schema.TextLine(
        title=_(u'URL'),
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


@implementer(IXMLQuery)
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
            response = urllib2.urlopen(self.url)
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
