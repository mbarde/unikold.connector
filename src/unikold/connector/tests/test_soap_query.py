# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
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

    def test_soap_query_connector(self):
        soapConnector = SOAPConnector(
            soap_test_url,
            soap_test_method,
            soap_test_method_parameter,
            24
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

    def test_soap_query_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.portal,
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
        self.assertTrue(
            fti.global_allow,
            u'{0} is not globally addable!'.format(fti.id)
        )
