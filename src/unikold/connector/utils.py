# -*- coding: utf-8 -*-
from zeep import Client
from zeep.transports import Transport


def getSOAPResponse(wsdlUrl, wsdlMethod, wsdlMethodParameter, timeout=10):
    data = False
    error = False

    try:
        transport = Transport(timeout=timeout)
        client = Client(wsdlUrl, transport=transport)
        data = getattr(client.service, wsdlMethod)(wsdlMethodParameter)
    except Exception as exc:
        error = str(exc) + '\n\nRaw answer:\n' + data
    finally:
        if data == 'False':
            error = 'Invalid SOAP response: ' + str(data)
            data = False
        return (data, error)
