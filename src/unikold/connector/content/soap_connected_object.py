# -*- coding: utf-8 -*-
# from plone.autoform import directives
from plone.dexterity.content import Item
from plone.supermodel import model
from zope import schema
from zope.interface import implementer
from zeep import Client
from lxml import etree
from AccessControl import Unauthorized
from zope.security import checkPermission
from unikold.connector import _


class ISOAPConnectedObject(model.Schema):

    wsdl_url = schema.TextLine(
        title=_(u'WSDL URL'),
        required=True
    )

    wsdl_method = schema.TextLine(
        title=_(u'WSDL Method'),
        required=True
    )

    soap_request = schema.Text(
        title=_(u'SOAP Request'),
        required=True
    )

    soap_response = schema.Text(
        title=_(u'SOAP Response'),
        required=False
    )


@implementer(ISOAPConnectedObject)
class SOAPConnectedObject(Item):

    def updateData(self):
        if not checkPermission('cmf.ModifyPortalContent', self):
            raise Unauthorized('You need ModifyPortalContent permission to execute this method')

        (data, err) = self.getXMLData(self.wsdl_url, self.wsdl_method, self.soap_request)
        if err is False:
            self.soap_response = etree.tostring(data)
            return data
        return False

    def getXMLData(self, wsdlUrl, wsdlMethod, xmlStr):
        data = False
        error = False

        try:
            client = Client(wsdlUrl)
            # dynamically call wsdl method like 'getXMLData'
            res = getattr(client.service, wsdlMethod)(xmlStr)
            val = res['_value_1'].encode('utf-8')

            if 'error' in val:
                error = val
            else:
                data = etree.fromstring(val)
        except Exception as exc:
            error = str(exc) + '\n\nRaw answer:\n' + val
        finally:
            return (data, error)
