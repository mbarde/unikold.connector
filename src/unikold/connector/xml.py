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

    def __init__(self, url, queryLifetimeInHours):
        self.url = url
        self.urlNormalized = idnormalizer.normalize(url)
        self.queryLifetime = timedelta(hours=queryLifetimeInHours)
        self.query = False
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

    # return folder containing the query object
    def getQueryFolder(self):
        return self.getXMLFolder()

    # return ID of query
    def getQueryID(self):
        return self.urlNormalized

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
        query = api.content.create(
            type=self.query_portal_type,
            title=title,
            id=id,
            container=container,
            **data)
        return query
