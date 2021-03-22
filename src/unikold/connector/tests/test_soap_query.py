# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from plone.i18n.normalizer import idnormalizer
from unikold.connector.content.soap_query import ISOAPQuery
from unikold.connector.soap import SOAPConnector
from unikold.connector.testing import UNIKOLD_CONNECTOR_INTEGRATION_TESTING
from unikold.connector.tests.config import soap_test_method
from unikold.connector.tests.config import soap_test_method_parameter
from unikold.connector.tests.config import soap_test_url
from zope.component import createObject
from zope.component import queryUtility

import unittest


try:
    from plone.dexterity.schema import portalTypeToSchemaName
except ImportError:
    # Plone < 5
    from plone.dexterity.utils import portalTypeToSchemaName  # noqa: F401


class SOAPQueryIntegrationTest(unittest.TestCase):

    layer = UNIKOLD_CONNECTOR_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_soap_query_schema(self):
        fti = queryUtility(IDexterityFTI, name='SOAPQuery')
        schema = fti.lookupSchema()
        self.assertEqual(ISOAPQuery, schema)

    def test_soap_query_fti(self):
        fti = queryUtility(IDexterityFTI, name='SOAPQuery')
        self.assertTrue(fti)

    def test_soap_query_factory(self):
        fti = queryUtility(IDexterityFTI, name='SOAPQuery')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            ISOAPQuery.providedBy(obj),
            u'ISOAPQuery not provided by {0}!'.format(
                obj,
            ),
        )

    def test_soap_query_adding(self):
        folderPath = api.portal.get_registry_record('unikold_connector.soap_queries_folder')
        folder = self.portal.restrictedTraverse(str(folderPath))
        setRoles(self.portal, TEST_USER_ID, ['Authenticated'])

        obj = api.content.create(
            container=folder,
            type='SOAPQuery',
            id='soap_query',
        )

        self.assertTrue(
            ISOAPQuery.providedBy(obj),
            u'ISOAPQuery not provided by {0}!'.format(
                obj.id,
            ),
        )

    def test_soap_query_globally_addable(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='SOAPQuery')
        self.assertFalse(
            fti.global_allow,
            u'{0} is globally addable!'.format(fti.id),
        )

    def test_excluded_from_search(self):
        types_not_searched = api.portal.get_registry_record('plone.types_not_searched')
        self.assertTrue('SOAPQuery' in types_not_searched)

    def test_soap_query_connector(self):
        soapConnector = SOAPConnector(
            soap_test_url,
            soap_test_method,
            soap_test_method_parameter,
            24,
        )

        query = soapConnector.getQuery()
        self.assertEqual(query.soap_response, None)

        data = soapConnector.get()
        self.assertEqual(data, 'True')

        self.assertEqual(query.soap_response, 'True')
        self.assertTrue(query.modified() > query.created())

        modifiedBefore = query.modified()
        soapConnector.get()
        self.assertEqual(modifiedBefore, query.modified())

        queryPath = list(soapConnector.getQuery().getPhysicalPath()[2:])

        expectedPath = [soapConnector.soapQueriesFolder.id]
        for part in soap_test_url.split('/'):
            if len(part) == 0:
                continue
            expectedPath.append(idnormalizer.normalize(part))
        expectedPath.append(idnormalizer.normalize(soap_test_method))
        expectedPath.append(idnormalizer.normalize(soap_test_method_parameter))

        self.assertEqual(queryPath, expectedPath)

    def test_soap_query_connector_fail_params(self):
        notExistingMethod = 'notexistingmethod'
        soapConnector = SOAPConnector(
            soap_test_url,
            notExistingMethod,
            '',
            24,
        )

        data = soapConnector.get()
        self.assertEqual(data, '')
        query = soapConnector.getQuery()
        self.assertTrue(notExistingMethod in query.soap_error)

    def test_soap_query_connector_fail_url(self):
        soapConnector = SOAPConnector(
            'http://127.0.0.1?WSDL',
            soap_test_method,
            soap_test_method_parameter,
            24,
        )

        data = soapConnector.get()
        self.assertEqual(data, '')
        query = soapConnector.getQuery()
        self.assertTrue('There is no default service defined' in query.soap_error)
