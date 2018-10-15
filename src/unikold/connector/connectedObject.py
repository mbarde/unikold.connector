# -*- coding: utf-8 -*-
from unikold.connector.interfaces import IConnectedObject
from zope.interface import implements
from zeep import Client
from lxml import etree


class ConnectedObjectSOAP():
    implements(IConnectedObject)

    wsdlUrl = ''

    def getXMLData(self, methodName):
        data = False
        error = False

        xmlStr = """\
            <SOAPDataService>
                <general>
                    <object>%s</object>
               </general>
            </SOAPDataService>""" % methodName

        try:
            client = Client(self.wsdlUrl)  # NOQA
            res = client.service.getDataXML(xmlStr)
            val = res['_value_1']
            if 'error' in val:
                error = val
            else:
                data = etree.fromstring(val)
        except:  # NOQA (catch all possible connection/retry exceptions)
            error = 'Can not connect to KLIPS server'
        finally:
            return (data, error)
