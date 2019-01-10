# -*- coding: utf-8 -*-
from plone.dexterity.content import Item
from plone.supermodel import model
from zope import schema
from zope.interface import implementer
from soap_connected_object import SOAPConnectedObject, ISOAPConnectedObject
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
class SOAPSearchObject(Item, SOAPConnectedObject):

    def updateData(self):
        data = super(SOAPConnectedObject, self).updateData()
        if data:
            print(data)
