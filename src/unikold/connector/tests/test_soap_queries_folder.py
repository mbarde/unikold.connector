# -*- coding: utf-8 -*-
from unikold.connector.testing import UNIKOLD_CONNECTOR_INTEGRATION_TESTING  # noqa
from plone import api
from plone.api.exc import InvalidParameterError
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import createObject
from zope.component import queryUtility

import unittest


try:
    from plone.dexterity.schema import portalTypeToSchemaName
except ImportError:
    # Plone < 5
    from plone.dexterity.utils import portalTypeToSchemaName


class SOAPQueriesFolderIntegrationTest(unittest.TestCase):

    layer = UNIKOLD_CONNECTOR_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_soap_queries_folder_schema(self):
        fti = queryUtility(IDexterityFTI, name='SOAPQueriesFolder')
        schema = fti.lookupSchema()
        schema_name = portalTypeToSchemaName('SOAPQueriesFolder')
        self.assertEqual(schema_name, schema.getName())

    def test_soap_queries_folder_fti(self):
        fti = queryUtility(IDexterityFTI, name='SOAPQueriesFolder')
        self.assertTrue(fti)

    def test_soap_queries_folder_factory(self):
        fti = queryUtility(IDexterityFTI, name='SOAPQueriesFolder')
        factory = fti.factory
        createObject(factory)

    def test_soap_queries_folder_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        api.content.create(
            container=self.portal,
            type='SOAPQueriesFolder',
            id='soap_queries_folder',
        )

    def test_soap_queries_folder_globally_addable(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='SOAPQueriesFolder')
        self.assertTrue(
            fti.global_allow,
            u'{0} is not globally addable!'.format(fti.id)
        )

    def test_soap_queries_folder_filter_content_type_true(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='SOAPQueriesFolder')
        portal_types = self.portal.portal_types
        parent_id = portal_types.constructContent(
            fti.id,
            self.portal,
            'soap_queries_folder_id',
            title='SOAPQueriesFolder container',
         )
        self.parent = self.portal[parent_id]
        with self.assertRaises(InvalidParameterError):
            api.content.create(
                container=self.parent,
                type='Document',
                title='My Content',
            )
