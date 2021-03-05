# -*- coding: utf-8 -*-
from datetime import timedelta
from plone import api
from plone.i18n.normalizer import idnormalizer
from unikold.connector.utils import createNestedFolders
from unikold.connector.utils import initSOAPQueriesFolder


class XMLConnector():
    query_portal_type = 'XMLQuery'

    def __init__(self, url, queryLifetimeInHours,
                 queryParams=[], basicAuthCredentials=(False, False),
                 excludeFromAutoUpdate=False):
        self.url = url
        self.queryParams = sorted(queryParams)
        self.urlNormalized = idnormalizer.normalize(url)
        self.queryLifetime = timedelta(hours=queryLifetimeInHours)
        self.query = False
        self.basicAuthCredentials = False
        self.excludeFromAutoUpdate = excludeFromAutoUpdate
        if basicAuthCredentials[0] and basicAuthCredentials[1]:
            self.basicAuthCredentials = basicAuthCredentials
        self.soapQueriesFolder = initSOAPQueriesFolder()

    def get(self, forceUpdate=False):
        if self.soapQueriesFolder is None:
            return None

        query = self.getQuery()
        query.getData(forceUpdate)  # make sure response is updated if neccessary
        return query.getXMLResponse()

    # return folder containing the query object
    def getQueryFolder(self):
        parts = self.url.split('/')
        curFolder = createNestedFolders(self.soapQueriesFolder, parts)
        if len(self.queryParams) == 0:
            return curFolder

        curFolder = createNestedFolders(curFolder, self.queryParams)
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
        query = queryFolder.get(queryID, None)
        if query is None or query.portal_type != self.query_portal_type:
            query = self.createQuery(queryID, queryID,
                                     queryFolder, additionalQueryData)

        self.query = query
        return query

    def createQuery(self, id, title, container, additionalQueryData=False):
        data = {
            'url': self.url,
            'lifetime': self.queryLifetime,
            'exclude_from_auto_update': self.excludeFromAutoUpdate,
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
