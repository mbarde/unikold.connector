# -*- coding: utf-8 -*-
from datetime import timedelta
from plone import api
from plone.i18n.normalizer import idnormalizer
from unikold.connector.utils import createNestedFolders
from unikold.connector.utils import initSOAPQueriesFolder


class LDAPSearchConnector(object):
    query_portal_type = 'LDAPSearchQuery'

    def __init__(self, address=None, port=None,
                 baseDN=None, searchFilter=None,
                 username=None, password=None,
                 queryLifetimeInHours=24, excludeFromAutoUpdate=False):
        self.queryLifetime = timedelta(hours=queryLifetimeInHours)
        self.query = False
        self.queryData = {
            'address': address,
            'port': port,
            'username': username,
            'password': password,
            'base_dn': baseDN,
            'filter': searchFilter,
        }

        # searchFilter has format: key=value
        [self.searchFilterKey, self.searchFilterValue] = searchFilter.split('=')

        self.excludeFromAutoUpdate = excludeFromAutoUpdate
        self.soapQueriesFolder = initSOAPQueriesFolder()

    def getAddress(self):
        if self.queryData['address'] is not None:
            return self.queryData['address']
        return api.portal.get_registry_record('unikold_connector_ldap.ldap_default_address')

    def getBaseDN(self):
        if self.queryData['base_dn'] is not None:
            return self.queryData['base_dn']
        return api.portal.get_registry_record('unikold_connector_ldap.ldap_default_base_dn')

    def get(self, forceUpdate=False):
        if self.soapQueriesFolder is None:
            return None

        query = self.getQuery()
        query.getData(forceUpdate)  # make sure response is updated if neccessary
        return query.getResults()

    # return folder containing the query object
    def getQueryFolder(self):
        parts = self.getAddress().split('/')
        parts += self.getBaseDN().split(',')
        parts.append(self.searchFilterKey)
        return createNestedFolders(self.soapQueriesFolder, parts)

    # return ID of query
    def getQueryID(self):
        return idnormalizer.normalize(self.searchFilterValue)

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
            'lifetime': self.queryLifetime,
            'exclude_from_auto_update': self.excludeFromAutoUpdate,
        }
        data.update(self.queryData)
        if additionalQueryData:
            data.update(additionalQueryData)

        query = api.content.create(
            type=self.query_portal_type,
            title=title,
            id=id,
            container=container,
            **data)
        return query
