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
        name = schema.getName()
        self.assertTrue(name.startswith('plone_'))
        self.assertTrue(name.endswith('_0_SOAPQueriesFolder'))
        schema_name = portalTypeToSchemaName('SOAPQueriesFolder')
        self.assertTrue(schema_name.startswith('plone_'))
        self.assertTrue(schema_name.endswith('_0_SOAPQueriesFolder'))

    def test_soap_queries_folder_fti(self):
        fti = queryUtility(IDexterityFTI, name='SOAPQueriesFolder')
        self.assertTrue(fti)

    def test_soap_queries_folder_factory(self):
        fti = queryUtility(IDexterityFTI, name='SOAPQueriesFolder')
        factory = fti.factory
        createObject(factory)

    def test_soap_queries_folder_adding(self):
        folderPath = api.portal.get_registry_record('unikold_connector.soap_queries_folder')
        folder = self.portal.restrictedTraverse(str(folderPath))
        setRoles(self.portal, TEST_USER_ID, ['Authenticated'])

        api.content.create(
            container=folder,
            type='SOAPQueriesFolder',
            id='soap_queries_folder',
        )

    def test_soap_queries_folder_globally_addable(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='SOAPQueriesFolder')
        self.assertFalse(
            fti.global_allow,
            u'{0} is globally addable!'.format(fti.id),
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

    def test_excluded_from_search(self):
        types_not_searched = api.portal.get_registry_record('plone.types_not_searched')
        self.assertTrue('SOAPQueriesFolder' in types_not_searched)
