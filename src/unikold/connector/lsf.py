# -*- coding: utf-8 -*-
from plone import api
from unikold.connector.soap import SOAPConnector


class LSFConnector(SOAPConnector):
    query_portal_type = 'LSFQuery'

    def __init__(self, soapRequest, queryLifetimeInHours):
        wsdlUrl = api.portal.get_registry_record('unikold_connector_lsf.lsf_wsdl_url')
        wsdlMethod = 'getDataXML'
        SOAPConnector.__init__(self, wsdlUrl, wsdlMethod,
                               soapRequest, queryLifetimeInHours)


class LSFSearchConnector(SOAPConnector):
    query_portal_type = 'LSFSearchQuery'

    def __init__(self, soapRequest, queryLifetimeInHours):
        wsdlUrl = api.portal.get_registry_record('unikold_connector_lsf.lsf_wsdl_search_url')
        wsdlMethod = 'search'
        SOAPConnector.__init__(self, wsdlUrl, wsdlMethod,
                               soapRequest, queryLifetimeInHours)

    # search query connector should return pre-parsed python list
    # of search results instead of plain SOAP response
    def get(self):
        query = self.getQuery()
        query.getData()
        return query.getSearchResults()
