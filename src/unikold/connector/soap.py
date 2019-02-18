# -*- coding: utf-8 -*-
from AccessControl.unauthorized import Unauthorized
from datetime import timedelta
from plone import api
from plone.i18n.normalizer import idnormalizer


class SOAPConnector():
    query_portal_type = 'SOAPQuery'

    def __init__(self, wsdlUrl, wsdlMethod, soapRequest, queryLifetimeInHours):
        self.wsdlUrl = wsdlUrl
        self.wsdlUrlNormalized = idnormalizer.normalize(wsdlUrl)
        self.wsdlMethod = wsdlMethod
        self.wsdlMethodNormalized = idnormalizer.normalize(wsdlMethod)
        self.soapRequest = soapRequest
        self.soapRequestNormalized = idnormalizer.normalize(soapRequest)
        self.queryLifetime = timedelta(hours=queryLifetimeInHours)
        self.query = False
        self.initSOAPQueriesFolder()

    def get(self, forceUpdate=False):
        if self.soapQueriesFolder is None:
            return None

        query = self.getQuery()
        return query.getData(forceUpdate)

    def initSOAPQueriesFolder(self):
        self.soapQueriesFolder = None

        # intentionally no try and except blocks here since we can not use the
        # SOAPConnector if we cant get the folder where queries are stored and cached
        soapQueriesPath = api.portal.get_registry_record('unikold_connector.soap_queries_folder')
        if soapQueriesPath is not None and len(soapQueriesPath) > 0:
            portal = api.portal.get()
            try:
                obj = portal.restrictedTraverse(str(soapQueriesPath))
                if obj.portal_type == 'SOAPQueriesFolder':
                    self.soapQueriesFolder = obj
            except (KeyError, Unauthorized):
                pass

    def getUrlFolder(self):
        urlFolder = getattr(self.soapQueriesFolder, self.wsdlUrlNormalized, None)
        if urlFolder is None:
            urlFolder = api.content.create(
                type='SOAPQueriesFolder',
                title=self.wsdlUrlNormalized,
                id=self.wsdlUrlNormalized,
                container=self.soapQueriesFolder)
        return urlFolder

    def getMethodFolder(self):
        urlFolder = self.getUrlFolder()
        methodFolder = getattr(urlFolder, self.wsdlMethodNormalized, None)
        if methodFolder is None:
            methodFolder = api.content.create(
                type='SOAPQueriesFolder',
                title=self.wsdlMethodNormalized,
                id=self.wsdlMethodNormalized,
                container=urlFolder)
        return methodFolder

    # return folder containing the query object
    def getQueryFolder(self):
        return self.getMethodFolder()

    # return ID of query
    def getQueryID(self):
        return self.soapRequestNormalized

    def getQuery(self, additionalQueryData=False):
        if self.soapQueriesFolder is None:
            return None
        if self.query:
            return self.query

        queryFolder = self.getQueryFolder()
        queryID = self.getQueryID()
        query = getattr(queryFolder, queryID, None)
        if query is None or query.portal_type != self.query_portal_type:
            query = self.createQuery(queryID, queryID,
                                     queryFolder, additionalQueryData)

        self.query = query
        return query

    def createQuery(self, id, title, container, additionalQueryData=False):
        data = {
            'wsdl_url': self.wsdlUrl,
            'wsdl_method': self.wsdlMethod,
            'wsdl_method_parameter': self.soapRequest,
            'lifetime': self.queryLifetime
        }
        if additionalQueryData:
            data.update(additionalQueryData)
        query = api.content.create(
            type=self.query_portal_type,
            title=title,
            id=id,
            container=container,
            **data)
        return query
