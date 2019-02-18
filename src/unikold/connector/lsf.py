# -*- coding: utf-8 -*-
from lxml import etree
from plone import api
from plone.i18n.normalizer import idnormalizer
from unikold.connector.soap import SOAPConnector


class LSFConnector(SOAPConnector):
    '''
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
    '''
    query_portal_type = 'LSFQuery'

    def __init__(self, objectType, conditions, queryLifetimeInHours, useAuthentication=True):
        self.useAuthentication = useAuthentication
        self.objectType = objectType
        self.objectTypeNormalized = idnormalizer.normalize(objectType)
        self.conditions = conditions
        self.conditionsNormalized = self.normalizeConditions(conditions)

        wsdlUrl = api.portal.get_registry_record('unikold_connector_lsf.lsf_wsdl_url')
        wsdlMethod = 'getDataXML'
        soapRequest = self.buildLSFSOAPRequest(objectType, conditions)
        SOAPConnector.__init__(self, wsdlUrl, wsdlMethod,
                               soapRequest, queryLifetimeInHours)

    def getQueryFolder(self):
        methodFolder = self.getMethodFolder()
        objectTypeFolder = getattr(methodFolder, self.objectTypeNormalized, None)
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

        query = self.getQuery({'use_authentication': self.useAuthentication})
        query.getData(forceUpdate)  # make sure response is updated if neccessary
        return query.getLSFResponse()

    def buildLSFSOAPRequest(self, objectType, conditions=[]):
        root = etree.Element('SOAPDataService')
        general = etree.SubElement(root, 'general')
        object = etree.SubElement(general, 'object')
        object.text = objectType

        if len(conditions) > 0:
            condition = etree.SubElement(root, 'condition')
            for param in conditions:
                key = param[0]
                value = param[1]
                el = etree.SubElement(condition, key)
                el.text = value

        return etree.tostring(root, pretty_print=True)

    def normalizeConditions(self, conditions):
        res = []
        for c in conditions:
            res.append(c[0] + '-' + c[1])
        result = '-'.join(res)
        return idnormalizer.normalize(result)


class LSFSearchConnector(SOAPConnector):
    query_portal_type = 'LSFSearchQuery'

    def __init__(self, soapRequest, queryLifetimeInHours, useAuthentication=True):
        self.useAuthentication = useAuthentication
        wsdlUrl = api.portal.get_registry_record('unikold_connector_lsf.lsf_wsdl_search_url')
        wsdlMethod = 'search'
        SOAPConnector.__init__(self, wsdlUrl, wsdlMethod,
                               soapRequest, queryLifetimeInHours)

    # search query connector should return pre-parsed python list
    # of search results instead of plain SOAP response
    def get(self, forceUpdate=False):
        if self.soapQueriesFolder is None:
            return []

        query = self.getQuery({'use_authentication': self.useAuthentication})
        query.getData(forceUpdate)  # make sure response is updated if neccessary
        return query.getSearchResults()
