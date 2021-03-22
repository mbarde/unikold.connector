# -*- coding: utf-8 -*-
from unikold.connector.content.lsf_query import ILSFQuery
from unikold.connector.content.lsf_query import LSFQuery
from zope.interface import implementer


class ILSFSearchQuery(ILSFQuery):
    pass


@implementer(ILSFSearchQuery)
class LSFSearchQuery(LSFQuery):

    # store search results as list of python objects
    def getSOAPResponse(self):
        (data, error) = super(LSFSearchQuery, self).getSOAPResponse()
        if error is False:
            searchResults = []
            lsfResponse = self.getLSFResponse()
            for obj in lsfResponse.iter('object'):
                result = {}
                for attr in obj.iter('attribute'):
                    name = attr.get('name')
                    value = attr.get('value')
                    result[name] = value
                searchResults.append(result)
            self.search_results = searchResults
        return (data, error)

    def getSearchResults(self):
        searchResults = getattr(self, 'search_results', None)
        if searchResults is not None:
            return self.search_results
        else:
            return []
