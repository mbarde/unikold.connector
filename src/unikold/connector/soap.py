# -*- coding: utf-8 -*-
from plone.i18n.normalizer import idnormalizer
from plone import api


class SOAPConnector():

    def __init__(self, wsdlUrl, wsdlMethod, soapRequest):
        self.wsdlUrl = wsdlUrl
        self.wsdlUrlNormalized = idnormalizer.normalize(wsdlUrl)
        self.wsdlMethod = wsdlMethod
        self.wsdlMethodNormalized = idnormalizer.normalize(wsdlMethod)
        self.soapRequest = soapRequest
        self.soapRequestNormalized = idnormalizer.normalize(soapRequest)

        self.initSOAPQueriesFolder()

    def get(self):
        query = self.getQuery()
        if query is None:
            # create query
            pass
        else:
            return query.getData()

    def initSOAPQueriesFolder(self):
        soapQueriesPath = '/Service/lsf-data'

        portal = api.portal.get()
        self.soapQueriesFolder = portal.restrictedTraverse(str(soapQueriesPath))

    def getQuery(self):
        urlFolder = getattr(self.soapQueriesFolder, self.wsdlUrlNormalized, None)
        if urlFolder is None:
            urlFolder = api.content.create(
                type='Folder',
                title=self.wsdlUrlNormalized,
                id=self.wsdlUrlNormalized,
                container=self.soapQueriesFolder)

        methodFolder = getattr(urlFolder, self.wsdlMethodNormalized, None)
        if methodFolder is not None:
            urlFolder = api.content.create(
                type='Folder',
                title=self.wsdlMethodNormalized,
                id=self.wsdlMethodNormalized,
                container=urlFolder)

        query = getattr(methodFolder, self.soapRequestNormalized, None)
        if query is not None:
            data = {
                'wsdl_url': self.wsdlUrl,
                'wsdl_method': self.wsdlMethod,
                'soap_request': self.soapRequest
            }
            urlFolder = api.content.create(
                type='SOAPQuery',
                title=self.soapRequestNormalized,
                id=self.soapRequestNormalized,
                container=methodFolder,
                **data)
