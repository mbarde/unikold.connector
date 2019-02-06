# -*- coding: utf-8 -*-
from plone import api
from zeep import Client
from zeep.transports import Transport


def getSOAPResponse(wsdlUrl, wsdlMethod, wsdlMethodParameter):
    data = False
    error = False

    timeout = api.portal.get_registry_record('unikold_connector.soap_timeout')
    if type(timeout) is not int:
        timeout = 10

    try:
        transport = Transport(timeout=timeout)
        client = Client(wsdlUrl, transport=transport)
        data = getattr(client.service, wsdlMethod)(wsdlMethodParameter)
    except Exception as exc:
        error = str(exc) + '\n\nRaw answer:\n' + str(data)
    finally:
        if data == 'False' or data is False:
            if error is False:
                error = 'Invalid SOAP response: ' + str(data)
            data = False

    return (data, error)
