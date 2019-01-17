# -*- coding: utf-8 -*-
from lxml import etree
from unikold.connector.content.soap_query import ISOAPQuery
from unikold.connector.content.soap_query import SOAPQuery
from zope.interface import implementer


class ILSFQuery(ISOAPQuery):
    pass


@implementer(ILSFQuery)
class LSFQuery(SOAPQuery):

    # responses from LSF have a certain structure
    # this method removes useless stuff and stores response additionally
    # as XML etree
    def getSOAPResponse(self, wsdlUrl, wsdlMethod, wsdlMethodParameter):
        (data, error) = super(LSFQuery, self).getSOAPResponse(
            wsdlUrl, wsdlMethod, wsdlMethodParameter
        )
        if error is False:
            val = data['_value_1'].encode('utf-8')

            if 'error' in val:
                error = val
            else:
                data = etree.fromstring(val)
                self.soap_response_xml = data
                data = etree.tostring(data)

        return (data, error)
