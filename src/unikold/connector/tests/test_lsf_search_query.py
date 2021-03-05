# -*- coding: utf-8 -*-
from lxml import etree
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from plone.i18n.normalizer import idnormalizer
from unikold.connector.content.lsf_search_query import ILSFSearchQuery  # NOQA E501
from unikold.connector.lsf import LSFSearchConnector
from unikold.connector.testing import UNIKOLD_CONNECTOR_INTEGRATION_TESTING  # noqa
from unikold.connector.tests.config import lsf_search_test_method_parameter
from unikold.connector.tests.config import lsf_wsdl_search_url
from zope.component import createObject
from zope.component import queryUtility

import unittest


try:
    from plone.dexterity.schema import portalTypeToSchemaName
except ImportError:
    # Plone < 5
    from plone.dexterity.utils import portalTypeToSchemaName  # noqa: F401


class LSFSearchQueryIntegrationTest(unittest.TestCase):

    layer = UNIKOLD_CONNECTOR_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_lsf_search_query_schema(self):
        fti = queryUtility(IDexterityFTI, name='LSFSearchQuery')
        schema = fti.lookupSchema()
        self.assertEqual(ILSFSearchQuery, schema)

    def test_lsf_search_query_fti(self):
        fti = queryUtility(IDexterityFTI, name='LSFSearchQuery')
        self.assertTrue(fti)

    def test_lsf_search_query_factory(self):
        fti = queryUtility(IDexterityFTI, name='LSFSearchQuery')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            ILSFSearchQuery.providedBy(obj),
            u'ILSFSearchQuery not provided by {0}!'.format(
                obj,
            ),
        )

    def test_lsf_search_query_adding(self):
        folderPath = api.portal.get_registry_record('unikold_connector.soap_queries_folder')
        folder = self.portal.restrictedTraverse(str(folderPath))
        setRoles(self.portal, TEST_USER_ID, ['Authenticated'])

        obj = api.content.create(
            container=folder,
            type='LSFSearchQuery',
            id='lsf_search_query',
        )

        self.assertTrue(
            ILSFSearchQuery.providedBy(obj),
            u'ILSFSearchQuery not provided by {0}!'.format(
                obj.id,
            ),
        )

    def test_lsf_search_query_globally_addable(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='LSFSearchQuery')
        self.assertFalse(
            fti.global_allow,
            u'{0} is globally addable!'.format(fti.id),
        )

    def test_excluded_from_search(self):
        types_not_searched = api.portal.get_registry_record('plone.types_not_searched')
        self.assertTrue('LSFSearchQuery' in types_not_searched)

    def test_lsf_search_query_connector(self):
        lsfSearchConnector = LSFSearchConnector(
            lsf_search_test_method_parameter, 24)

        query = lsfSearchConnector.getQuery()
        self.assertEqual(query.soap_response, None)
        self.assertEqual(getattr(query, 'search_results', None), None)

        lsfResponse = query.getLSFResponse()
        self.assertTrue(type(lsfResponse) is etree._Element)
        self.assertTrue(len(lsfResponse) == 0)

        data = lsfSearchConnector.get()
        self.assertTrue(len(data) > 0)
        self.assertTrue(type(data[0]) is dict)

        lsfResponse = query.getLSFResponse()
        self.assertTrue(type(lsfResponse) is etree._Element)
        self.assertTrue(len(lsfResponse) > 0)

        self.assertNotEqual(getattr(query, 'search_results', None), None)
        self.assertTrue(type(query.search_results) is list)

        self.assertTrue(query.modified() > query.created())

        modifiedBefore = query.modified()
        lsfSearchConnector.get()
        self.assertEqual(modifiedBefore, query.modified())

        queryPath = list(lsfSearchConnector.getQuery().getPhysicalPath()[2:])

        expectedPath = [lsfSearchConnector.soapQueriesFolder.id]
        wsdlUrl = api.portal.get_registry_record('unikold_connector_lsf.lsf_wsdl_search_url')
        for part in wsdlUrl.split('/'):
            if len(part) == 0:
                continue
            expectedPath.append(idnormalizer.normalize(part))

        wsdlMethod = 'search'
        expectedPath.append(idnormalizer.normalize(wsdlMethod))
        expectedPath.append(idnormalizer.normalize(lsf_search_test_method_parameter))

        self.assertEqual(queryPath, expectedPath)

    def test_lsf_search_query_connector_fail_params(self):
        lsfSearchConnector = LSFSearchConnector(
            'uselessparameter', 24)

        data = lsfSearchConnector.get()
        self.assertEqual(data, [])
        query = lsfSearchConnector.getQuery()
        self.assertTrue('java.lang.NullPointerException' in query.soap_error)

    def test_lsf_search_query_connector_fail_url(self):
        api.portal.set_registry_record('unikold_connector_lsf.lsf_wsdl_search_url',
                                       u'http://127.0.0.1?WSDL')

        lsfSearchConnector = LSFSearchConnector(
            lsf_search_test_method_parameter, 24)

        data = lsfSearchConnector.get()
        self.assertEqual(data, [])
        query = lsfSearchConnector.getQuery()
        self.assertTrue('There is no default service defined' in query.soap_error)

        api.portal.set_registry_record('unikold_connector_lsf.lsf_wsdl_search_url',
                                       lsf_wsdl_search_url)
