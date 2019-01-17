# -*- coding: utf-8 -*-
from unikold.connector.content.s_o_a_p_query import ISOAPQuery  # NOQA E501
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
    from plone.dexterity.utils import portalTypeToSchemaName


class SOAPQueryIntegrationTest(unittest.TestCase):

    layer = UNIKOLD_CONNECTOR_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_ct_s_o_a_p_query_schema(self):
        fti = queryUtility(IDexterityFTI, name='SOAPQuery')
        schema = fti.lookupSchema()
        self.assertEqual(ISOAPQuery, schema)

    def test_ct_s_o_a_p_query_fti(self):
        fti = queryUtility(IDexterityFTI, name='SOAPQuery')
        self.assertTrue(fti)

    def test_ct_s_o_a_p_query_factory(self):
        fti = queryUtility(IDexterityFTI, name='SOAPQuery')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            ISOAPQuery.providedBy(obj),
            u'ISOAPQuery not provided by {0}!'.format(
                obj,
            ),
        )

    def test_ct_s_o_a_p_query_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.portal,
            type='SOAPQuery',
            id='s_o_a_p_query',
        )

        self.assertTrue(
            ISOAPQuery.providedBy(obj),
            u'ISOAPQuery not provided by {0}!'.format(
                obj.id,
            ),
        )

    def test_ct_s_o_a_p_query_globally_addable(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='SOAPQuery')
        self.assertTrue(
            fti.global_allow,
            u'{0} is not globally addable!'.format(fti.id)
        )
