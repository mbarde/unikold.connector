# -*- coding: utf-8 -*-
# from plone.dexterity.content import Item
from plone.supermodel import model
from zope import schema
from zope.interface import implementer
from unikold.connector.content.soap_connected_object import SOAPConnectedObject
from unikold.connector.content.soap_connected_object import ISOAPConnectedObject
from unikold.connector import _


class ISOAPSearchObject(model.Schema, ISOAPConnectedObject):

    wsdl_url = schema.TextLine(
        title=_(u'WSDL URL'),
        required=True,
        default=u'https://klips.uni-koblenz.de/qisserver/services/soapsearch?WSDL'

    )

    wsdl_method = schema.TextLine(
        title=_(u'WSDL Method'),
        required=True,
        default=u'search'
    )

    soap_request = schema.Text(
        title=_(u'SOAP Request'),
        required=True,
        default=u'<search><object></object><expression></expression></search>'
    )


@implementer(ISOAPSearchObject)
class SOAPSearchObject(SOAPConnectedObject):

    def updateData(self):
        data = super(SOAPSearchObject, self).updateData()
        if data is not False:
            searchResults = []
            for obj in data.iter('object'):
                result = {}
                for attr in obj.iter('attribute'):
                    name = attr.get('name')
                    value = attr.get('value')
                    result[name] = value
                searchResults.append(result)
            self.search_results = searchResults
            return data
        return False
