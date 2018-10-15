# -*- coding: utf-8 -*-
from unikold.connector.content.test_type import ITestType  # NOQA E501
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


class TestTypeIntegrationTest(unittest.TestCase):

    layer = UNIKOLD_CONNECTOR_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_ct_test_type_schema(self):
        fti = queryUtility(IDexterityFTI, name='TestType')
        schema = fti.lookupSchema()
        self.assertEqual(ITestType, schema)

    def test_ct_test_type_fti(self):
        fti = queryUtility(IDexterityFTI, name='TestType')
        self.assertTrue(fti)

    def test_ct_test_type_factory(self):
        fti = queryUtility(IDexterityFTI, name='TestType')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            ITestType.providedBy(obj),
            u'ITestType not provided by {0}!'.format(
                obj,
            ),
        )

    def test_ct_test_type_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.portal,
            type='TestType',
            id='test_type',
        )

        self.assertTrue(
            ITestType.providedBy(obj),
            u'ITestType not provided by {0}!'.format(
                obj.id,
            ),
        )

    def test_ct_test_type_globally_addable(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='TestType')
        self.assertTrue(
            fti.global_allow,
            u'{0} is not globally addable!'.format(fti.id)
        )
