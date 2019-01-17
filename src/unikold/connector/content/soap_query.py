# -*- coding: utf-8 -*-
# from plone.autoform import directives
from DateTime import DateTime
from datetime import timedelta
from plone.dexterity.content import Item
from plone.supermodel import model
from unikold.connector import _
from zeep import Client
from zope import schema
from zope.interface import implementer


class ISOAPQuery(model.Schema):

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

    lifetime = schema.Timedelta(
        title=_(u'Lifetime'),
        required=True,
        default=timedelta(hours=48)
    )


@implementer(ISOAPQuery)
class SOAPQuery(Item):

    def getData(self):
        # update data if there has not been a response yet ...
        if self.soap_response is None:
            self.updateData()
        else:
            # ... or if lifetime of last update expired
            now = DateTime().asdatetime()
            modified = self.modified().asdatetime()
            if now > modified + self.lifetime:
                self.updateData()

        return self.soap_response

    def updateData(self):
        (data, err) = self.getXMLData(self.wsdl_url, self.wsdl_method, self.soap_request)
        if err is False:
            self.soap_response = str(data)
            self.setModificationDate(DateTime())
            return data
        return False

    def getXMLData(self, wsdlUrl, wsdlMethod, xmlStr):
        data = False
        error = False

        try:
            client = Client(wsdlUrl)
            # dynamically call wsdl method like 'getXMLData'
            data = getattr(client.service, wsdlMethod)(xmlStr)
        except Exception as exc:
            error = str(exc) + '\n\nRaw answer:\n' + data
        finally:
            return (data, error)
