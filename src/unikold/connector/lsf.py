# -*- coding: utf-8 -*-
from plone import api
from plone.i18n.normalizer import idnormalizer
from unikold.connector.soap import SOAPConnector
from unikold.connector.utils_lsf import buildLSFSOAPRequest


class LSFConnector(SOAPConnector):
    """
        A LSF `getDataXML` request always consists of an object and conditions,
        for example:

        getDataXML("
            <SOAPDataService>
              <general>
                <object>StudentMinimalType</object>
              </general>
              <condition>
                <id>211100718</id>
              </condition>
            </SOAPDataService>
        ")

        Here user just needs to specify those values and LSFConnector will create
        correct XML structure.
    """
    query_portal_type = 'LSFQuery'

    def __init__(self, objectType, conditions, queryLifetimeInHours,
                 useAuthentication=True, excludeFromAutoUpdate=False):
        self.useAuthentication = useAuthentication
        self.objectType = objectType
        self.objectTypeNormalized = idnormalizer.normalize(objectType)
        self.conditions = conditions
        self.conditionsNormalized = self.normalizeConditions(conditions)

        wsdlUrl = api.portal.get_registry_record('unikold_connector_lsf.lsf_wsdl_url')
        wsdlMethod = 'getDataXML'
        soapRequest = buildLSFSOAPRequest(objectType, conditions)
        SOAPConnector.__init__(self, wsdlUrl, wsdlMethod,
                               soapRequest, queryLifetimeInHours,
                               excludeFromAutoUpdate)

    def getQueryFolder(self):
        methodFolder = self.getMethodFolder()
        objectTypeFolder = methodFolder.get(self.objectTypeNormalized, None)
        if objectTypeFolder is None:
            objectTypeFolder = api.content.create(
                type='SOAPQueriesFolder',
                title=self.objectTypeNormalized,
                id=self.objectTypeNormalized,
                container=methodFolder)
        return objectTypeFolder

    def getQueryID(self):
        return self.conditionsNormalized

    # return LSF result as lxml.etree object
    def get(self, forceUpdate=False):
        if self.soapQueriesFolder is None:
            return None

        query = self.getQuery()
        query.getData(forceUpdate)  # make sure response is updated if neccessary
        return query.getLSFResponse()

    # extend method to ensure `use_authentication` property is set correctly
    def createQuery(self, id, title, container, additionalQueryData=False):
        if additionalQueryData is False:
            additionalQueryData = {}
        additionalQueryData['use_authentication'] = self.useAuthentication
        return super(LSFConnector, self).createQuery(
            id, title, container, additionalQueryData)

    def normalizeConditions(self, conditions):
        res = []
        for c in conditions:
            key = c[0]
            val = c[1]
            if not isinstance(key, str):
                key = key.decode()
            if not isinstance(val, str):
                val = val.decode()
            res.append(key + '-' + val)
        result = '-'.join(res)
        return idnormalizer.normalize(result)


class LSFSearchConnector(SOAPConnector):
    query_portal_type = 'LSFSearchQuery'

    def __init__(self, soapRequest, queryLifetimeInHours,
                 useAuthentication=True, excludeFromAutoUpdate=False):
        self.useAuthentication = useAuthentication
        wsdlUrl = api.portal.get_registry_record('unikold_connector_lsf.lsf_wsdl_search_url')
        wsdlMethod = 'search'
        SOAPConnector.__init__(self, wsdlUrl, wsdlMethod,
                               soapRequest, queryLifetimeInHours,
                               excludeFromAutoUpdate)

    # search query connector should return pre-parsed python list
    # of search results instead of plain SOAP response
    def get(self, forceUpdate=False):
        if self.soapQueriesFolder is None:
            return []

        query = self.getQuery({'use_authentication': self.useAuthentication})
        query.getData(forceUpdate)  # make sure response is updated if neccessary
        return query.getSearchResults()
