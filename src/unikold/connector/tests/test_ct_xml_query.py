# -*- coding: utf-8 -*-
from unikold.connector.content.xml_query import IXMLQuery  # NOQA E501
from unikold.connector.testing import UNIKOLD_CONNECTOR_INTEGRATION_TESTING  # noqa
from plone import api
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
    from plone.dexterity.utils import portalTypeToSchemaName  # noqa: F401


class XMLQueryIntegrationTest(unittest.TestCase):

    layer = UNIKOLD_CONNECTOR_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_ct_xml_query_schema(self):
        fti = queryUtility(IDexterityFTI, name='XMLQuery')
        schema = fti.lookupSchema()
        self.assertEqual(IXMLQuery, schema)

    def test_ct_xml_query_fti(self):
        fti = queryUtility(IDexterityFTI, name='XMLQuery')
        self.assertTrue(fti)

    def test_ct_xml_query_factory(self):
        fti = queryUtility(IDexterityFTI, name='XMLQuery')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            IXMLQuery.providedBy(obj),
            u'IXMLQuery not provided by {0}!'.format(
                obj,
            ),
        )

    def test_ct_xml_query_adding(self):
        folderPath = api.portal.get_registry_record('unikold_connector.soap_queries_folder')
        folder = self.portal.restrictedTraverse(str(folderPath))
        setRoles(self.portal, TEST_USER_ID, ['Authenticated'])

        obj = api.content.create(
            container=folder,
            type='XMLQuery',
            id='xml_query',
        )

        self.assertTrue(
            IXMLQuery.providedBy(obj),
            u'IXMLQuery not provided by {0}!'.format(
                obj.id,
            ),
        )

    def test_ct_xml_query_globally_not_addable(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='XMLQuery')
        self.assertFalse(
            fti.global_allow,
            u'{0} is globally addable!'.format(fti.id)
        )
