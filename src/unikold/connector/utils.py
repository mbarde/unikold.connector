# -*- coding: utf-8 -*-
from plone import api
from plone.i18n.normalizer import idnormalizer
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


# create nested folder structure within `root`
# provided by array `folderNames`
# (does nothing of strcuture already exists)
def createNestedFolders(container, folderNames):
    curContainer = container
    for folderName in folderNames:
        if len(folderName) == 0:
            continue
        normalizedName = idnormalizer.normalize(folderName)

        # make sure first char is not a '_'
        # (for some reason idnormalizer does not check that)
        if len(normalizedName) == 0:
            continue
        while '_' == normalizedName[0]:
            normalizedName = normalizedName[1:]
        if len(normalizedName) == 0:
            continue

        curFolder = curContainer.get(normalizedName, None)
        if curFolder is None:
            curFolder = api.content.create(
                type='SOAPQueriesFolder',
                title=normalizedName,
                id=normalizedName,
                container=curContainer)
        curContainer = curFolder
    return curContainer
