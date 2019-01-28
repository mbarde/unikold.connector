# -*- coding: utf-8 -*-
from unikold.connector.content.lsf_query import ILSFQuery
from unikold.connector.content.lsf_query import LSFQuery
from zope.interface import implementer


class ILSFSearchQuery(ILSFQuery):
    pass


@implementer(ILSFSearchQuery)
class LSFSearchQuery(LSFQuery):

    # store search results as list of python objects
    def getSOAPResponse(self, wsdlUrl, wsdlMethod, wsdlMethodParameter):
        (data, error) = super(LSFSearchQuery, self).getSOAPResponse(
            wsdlUrl, wsdlMethod, wsdlMethodParameter
        )
        if error is False and hasattr(self, 'soap_response_xml'):
            searchResults = []
            for obj in self.soap_response_xml.iter('object'):
                result = {}
                for attr in obj.iter('attribute'):
                    name = attr.get('name')
                    value = attr.get('value')
                    result[name] = value
                searchResults.append(result)
            self.search_results = searchResults
        return (data, error)

    def getSearchResults(self):
        if hasattr(self, 'search_results'):
            return self.search_results
        else:
            return []
