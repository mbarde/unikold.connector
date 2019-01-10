# -*- coding: utf-8 -*-
from unikold.connector.content.s_o_a_p_connected_object import ISOAPConnectedObject  # NOQA E501
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


class SOAPConnectedObjectIntegrationTest(unittest.TestCase):

    layer = UNIKOLD_CONNECTOR_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_ct_s_o_a_p_connected_object_schema(self):
        fti = queryUtility(IDexterityFTI, name='SOAPConnectedObject')
        schema = fti.lookupSchema()
        self.assertEqual(ISOAPConnectedObject, schema)

    def test_ct_s_o_a_p_connected_object_fti(self):
        fti = queryUtility(IDexterityFTI, name='SOAPConnectedObject')
        self.assertTrue(fti)

    def test_ct_s_o_a_p_connected_object_factory(self):
        fti = queryUtility(IDexterityFTI, name='SOAPConnectedObject')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            ISOAPConnectedObject.providedBy(obj),
            u'ISOAPConnectedObject not provided by {0}!'.format(
                obj,
            ),
        )

    def test_ct_s_o_a_p_connected_object_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.portal,
            type='SOAPConnectedObject',
            id='s_o_a_p_connected_object',
        )

        self.assertTrue(
            ISOAPConnectedObject.providedBy(obj),
            u'ISOAPConnectedObject not provided by {0}!'.format(
                obj.id,
            ),
        )

    def test_ct_s_o_a_p_connected_object_globally_addable(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='SOAPConnectedObject')
        self.assertTrue(
            fti.global_allow,
            u'{0} is not globally addable!'.format(fti.id)
        )
