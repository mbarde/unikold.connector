# -*- coding: utf-8 -*-
from datetime import timedelta
from plone import api
from plone.i18n.normalizer import idnormalizer
from unikold.connector.utils import createNestedFolders
from unikold.connector.utils import initSOAPQueriesFolder


class SOAPConnector(object):
    query_portal_type = 'SOAPQuery'

    def __init__(self, wsdlUrl, wsdlMethod,
                 soapRequest, queryLifetimeInHours, excludeFromAutoUpdate=False):
        self.wsdlUrl = wsdlUrl
        self.wsdlUrlNormalized = idnormalizer.normalize(wsdlUrl)
        self.wsdlMethod = wsdlMethod
        self.wsdlMethodNormalized = idnormalizer.normalize(wsdlMethod)
        self.soapRequest = soapRequest
        self.soapRequestNormalized = idnormalizer.normalize(soapRequest)
        self.queryLifetime = timedelta(hours=queryLifetimeInHours)
        self.excludeFromAutoUpdate = excludeFromAutoUpdate
        self.query = False
        self.soapQueriesFolder = initSOAPQueriesFolder()

    def get(self, forceUpdate=False):
        if self.soapQueriesFolder is None:
            return None

        query = self.getQuery()
        return query.getData(forceUpdate)

    def getMethodFolder(self):
        parts = self.wsdlUrl.split('/')
        parts.append(self.wsdlMethodNormalized)
        return createNestedFolders(self.soapQueriesFolder, parts)

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
        query = queryFolder.get(queryID, None)
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
            'lifetime': self.queryLifetime,
            'exclude_from_auto_update': self.excludeFromAutoUpdate,
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
