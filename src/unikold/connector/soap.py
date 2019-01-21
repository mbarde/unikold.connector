# -*- coding: utf-8 -*-
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

        self.initSOAPQueriesFolder()

    def get(self):
        query = self.getQuery()
        return query.getData()

    def initSOAPQueriesFolder(self):
        # intentionally no try and except blocks here since we can not use the
        # SOAPConnector if we cant get the folder where queries are stored and cached
        soapQueriesPath = api.portal.get_registry_record('unikold_connector.soap_queries_folder')
        portal = api.portal.get()
        if soapQueriesPath is None or len(soapQueriesPath) == 0:
            # if no path is specified simply create folder on nav root
            portalRoot = api.portal.get_navigation_root(portal)
            self.soapQueriesFolder = api.content.create(
                type='Folder',
                title='SOAP Queries',
                container=portalRoot)
            api.portal.set_registry_record(
                'unikold_connector.soap_queries_folder',
                u'/'.join(self.soapQueriesFolder.getPhysicalPath())
            )
        else:
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
        if query is None or query.portal_type != self.query_portal_type:
            data = {
                'wsdl_url': self.wsdlUrl,
                'wsdl_method': self.wsdlMethod,
                'wsdl_method_parameter': self.soapRequest,
                'lifetime': self.queryLifetime
            }
            query = api.content.create(
                type=self.query_portal_type,
                title=self.soapRequestNormalized,
                id=self.soapRequestNormalized,
                container=methodFolder,
                **data)

        return query
