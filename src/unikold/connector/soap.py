# -*- coding: utf-8 -*-
from plone.i18n.normalizer import idnormalizer
from plone import api
from datetime import timedelta


class SOAPConnector():

    def __init__(self, wsdlUrl, wsdlMethod, soapRequest, queryLifetimeInHours):
        self.wsdlUrl = wsdlUrl
        self.wsdlUrlNormalized = idnormalizer.normalize(wsdlUrl)
        self.wsdlMethod = wsdlMethod
        self.wsdlMethodNormalized = idnormalizer.normalize(wsdlMethod)
        self.soapRequest = soapRequest
        self.soapRequestNormalized = idnormalizer.normalize(soapRequest)
        self.queryLifetime = timedelta(hours=queryLifetimeInHours)

        self.initSOAPQueriesFolder()

    def get(self):
        query = self.getQuery()
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
        if methodFolder is None:
            methodFolder = api.content.create(
                type='Folder',
                title=self.wsdlMethodNormalized,
                id=self.wsdlMethodNormalized,
                container=urlFolder)

        query = getattr(methodFolder, self.soapRequestNormalized, None)
        if query is None:
            data = {
                'wsdl_url': self.wsdlUrl,
                'wsdl_method': self.wsdlMethod,
                'soap_request': self.soapRequest,
                'lifetime': self.queryLifetime
            }
            query = api.content.create(
                type='SOAPQuery',
                title=self.soapRequestNormalized,
                id=self.soapRequestNormalized,
                container=methodFolder,
                **data)

        return query

    def getSearchResults(self, data):
        searchResults = []
        for obj in data.iter('object'):
            result = {}
            for attr in obj.iter('attribute'):
                name = attr.get('name')
                value = attr.get('value')
                result[name] = value
            searchResults.append(result)
        self.search_results = searchResults
        return data
