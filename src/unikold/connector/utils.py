# -*- coding: utf-8 -*-
from zeep import Client
from zeep.transports import Transport


def getSOAPResponse(wsdlUrl, wsdlMethod, wsdlMethodParameter):
    data = False
    error = False

    try:
        transport = Transport(timeout=10)  # 10 sec.
        client = Client(wsdlUrl, transport=transport)
        data = getattr(client.service, wsdlMethod)(wsdlMethodParameter)
    except Exception as exc:
        error = str(exc) + '\n\nRaw answer:\n' + data
    finally:
        return (data, error)
