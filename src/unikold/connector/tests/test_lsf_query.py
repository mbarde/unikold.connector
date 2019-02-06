# -*- coding: utf-8 -*-
from lxml import etree
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from unikold.connector.content.lsf_query import ILSFQuery
from unikold.connector.lsf import LSFConnector
from unikold.connector.testing import UNIKOLD_CONNECTOR_INTEGRATION_TESTING
from unikold.connector.tests.config import lsf_auth_test_conditions
from unikold.connector.tests.config import lsf_auth_test_object_type
from unikold.connector.tests.config import lsf_test_conditions
from unikold.connector.tests.config import lsf_test_object_type
from unikold.connector.tests.config import lsf_wsdl_url
from zope.component import createObject
from zope.component import queryUtility

import unittest


try:
    from plone.dexterity.schema import portalTypeToSchemaName
except ImportError:
    # Plone < 5
    from plone.dexterity.utils import portalTypeToSchemaName  # noqa: F401


class LSFQueryIntegrationTest(unittest.TestCase):

    layer = UNIKOLD_CONNECTOR_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_lsf_query_schema(self):
        fti = queryUtility(IDexterityFTI, name='LSFQuery')
        schema = fti.lookupSchema()
        self.assertEqual(ILSFQuery, schema)

    def test_lsf_query_fti(self):
        fti = queryUtility(IDexterityFTI, name='LSFQuery')
        self.assertTrue(fti)

    def test_lsf_query_factory(self):
        fti = queryUtility(IDexterityFTI, name='LSFQuery')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            ILSFQuery.providedBy(obj),
            u'ILSFQuery not provided by {0}!'.format(
                obj,
            ),
        )

    def test_lsf_query_adding(self):
        folderPath = api.portal.get_registry_record('unikold_connector.soap_queries_folder')
        folder = self.portal.restrictedTraverse(str(folderPath))
        setRoles(self.portal, TEST_USER_ID, ['Authenticated'])

        obj = api.content.create(
            container=folder,
            type='LSFQuery',
            id='lsf_query',
        )

        self.assertTrue(
            ILSFQuery.providedBy(obj),
            u'ILSFQuery not provided by {0}!'.format(
                obj.id,
            ),
        )

    def test_lsf_query_globally_addable(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='LSFQuery')
        self.assertFalse(
            fti.global_allow,
            u'{0} is globally addable!'.format(fti.id)
        )

    def test_excluded_from_search(self):
        types_not_searched = api.portal.get_registry_record('plone.types_not_searched')
        self.assertTrue('LSFQuery' in types_not_searched)

    def test_lsf_query_connector(self):
        lsfConnector = LSFConnector(
            lsf_test_object_type, lsf_test_conditions, 24, False)

        query = lsfConnector.getQuery()
        self.assertEqual(query.soap_response, None)
        self.assertTrue(query, 'use_authentication')

        lsfResponse = query.getLSFResponse()
        self.assertTrue(type(lsfResponse) is etree._Element)
        self.assertTrue(len(lsfResponse) == 0)

        data = lsfConnector.get()
        self.assertTrue(len(data) > 0)

        lsfResponse = query.getLSFResponse()
        self.assertTrue(type(lsfResponse) is etree._Element)
        self.assertTrue(len(lsfResponse) > 0)

        self.assertTrue(query.modified() > query.created())

        modifiedBefore = query.modified()
        lsfConnector.get()
        self.assertEqual(modifiedBefore, query.modified())

        lsfConnector.get(True)  # force update
        self.assertTrue(modifiedBefore < query.modified())

    def test_lsf_query_connector_with_auth(self):
        lsfConnector = LSFConnector(lsf_auth_test_object_type, lsf_auth_test_conditions, 0, False)
        data = lsfConnector.get()
        self.assertTrue('no user rights' in etree.tostring(data))
        self.assertTrue(len(data) == 0)

        api.content.delete(lsfConnector.getQuery())

        lsfConnector = LSFConnector(lsf_auth_test_object_type, lsf_auth_test_conditions, 0, True)
        data = lsfConnector.get()
        self.assertTrue('no user rights' not in etree.tostring(data))
        self.assertTrue(len(data) > 0)

    def test_lsf_query_connector_fail_params(self):
        lsfConnector = LSFConnector(
            'anotexistingtype', lsf_test_conditions, 24, False)

        data = lsfConnector.get()
        self.assertEqual(data.tag, 'xml-syntax-error')
        query = lsfConnector.getQuery()
        self.assertEqual(query.soap_error, 'error in soap-request')

    def test_lsf_query_connector_fail_url(self):
        api.portal.set_registry_record('unikold_connector_lsf.lsf_wsdl_url',
                                       u'http://127.0.0.1?WSDL')

        lsfConnector = LSFConnector(
            lsf_test_object_type, lsf_test_conditions, 24, False)

        data = lsfConnector.get()
        self.assertEqual(data.tag, 'xml-syntax-error')
        query = lsfConnector.getQuery()
        self.assertTrue('Max retries exceeded' in query.soap_error)

        api.portal.set_registry_record('unikold_connector_lsf.lsf_wsdl_url', lsf_wsdl_url)
