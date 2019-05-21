# -*- coding: utf-8 -*-
from AccessControl.unauthorized import Unauthorized
from datetime import timedelta
from plone import api
from plone.i18n.normalizer import idnormalizer


class XMLConnector():
    query_portal_type = 'XMLQuery'

    # XML queries are stored in separate folder within
    # the root SOAPQueriesFolder:
    xmlFolderName = 'xml'

    def __init__(self, url, queryLifetimeInHours,
                 queryParams=[], basicAuthCredentials=(False, False)):
        self.url = url
        self.queryParams = sorted(queryParams)
        self.urlNormalized = idnormalizer.normalize(url)
        self.queryLifetime = timedelta(hours=queryLifetimeInHours)
        self.query = False
        self.basicAuthCredentials = False
        if basicAuthCredentials[0] and basicAuthCredentials[1]:
            self.basicAuthCredentials = basicAuthCredentials
        self.initSOAPQueriesFolder()

    def get(self, forceUpdate=False):
        if self.soapQueriesFolder is None:
            return None

        query = self.getQuery()
        query.getData(forceUpdate)  # make sure response is updated if neccessary
        return query.getXMLResponse()

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

    def getXMLFolder(self):
        xmlFolder = getattr(self.soapQueriesFolder, self.xmlFolderName, None)
        if xmlFolder is None:
            xmlFolder = api.content.create(
                type='SOAPQueriesFolder',
                title=self.xmlFolderName,
                id=self.xmlFolderName,
                container=self.soapQueriesFolder)
        return xmlFolder

    def getURLFolder(self):
        xmlFolder = self.getXMLFolder()
        urlFolder = getattr(xmlFolder, self.urlNormalized, None)
        if urlFolder is None:
            urlFolder = api.content.create(
                type='SOAPQueriesFolder',
                title=self.urlNormalized,
                id=self.urlNormalized,
                container=xmlFolder)
        return urlFolder

    # return folder containing the query object
    def getQueryFolder(self):
        urlFolder = self.getURLFolder()
        if len(self.queryParams) == 0:
            return urlFolder

        curFolder = urlFolder
        for param in self.queryParams:
            paramFolderName = idnormalizer.normalize(param)
            paramFolder = getattr(curFolder, paramFolderName, None)
            if paramFolder is None:
                paramFolder = api.content.create(
                    type='SOAPQueriesFolder',
                    title=paramFolderName,
                    id=paramFolderName,
                    container=curFolder)
            curFolder = paramFolder

        return curFolder

    # return ID of query
    def getQueryID(self):
        return 'xmlquery'

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
            'url': self.url,
            'lifetime': self.queryLifetime
        }
        if additionalQueryData:
            data.update(additionalQueryData)
        if len(self.queryParams) > 0:
            data['query_params'] = self.queryParams
        if self.basicAuthCredentials:
            data['basic_auth_username'] = self.basicAuthCredentials[0]
            data['basic_auth_password'] = self.basicAuthCredentials[1]
        query = api.content.create(
            type=self.query_portal_type,
            title=title,
            id=id,
            container=container,
            **data)
        return query
