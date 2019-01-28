# -*- coding: utf-8 -*-
from lxml import etree
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from unikold.connector.content.lsf_query import ILSFQuery
from unikold.connector.lsf import LSFConnector
from unikold.connector.testing import UNIKOLD_CONNECTOR_INTEGRATION_TESTING
from unikold.connector.tests.config import lsf_auth_password
from unikold.connector.tests.config import lsf_auth_username
from unikold.connector.tests.config import lsf_test_method_parameter
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

        # set registry values user has to set via controlpanel
        registry = self.portal.portal_registry
        registry.records['unikold_connector_lsf.lsf_wsdl_url']._set_value(lsf_wsdl_url)
        registry.records['unikold_connector_lsf.lsf_auth_username']._set_value(lsf_auth_username)
        registry.records['unikold_connector_lsf.lsf_auth_password']._set_value(lsf_auth_password)

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

    def test_lsf_query_connector(self):
        lsfConnector = LSFConnector(
            lsf_test_method_parameter, 24, False)

        query = lsfConnector.getQuery()
        self.assertEqual(query.soap_response, None)
        self.assertFalse(hasattr(query, 'soap_response_xml'))
        self.assertTrue(query, 'use_authentication')

        data = lsfConnector.get()
        self.assertTrue(len(data) > 0)

        self.assertTrue(hasattr(query, 'soap_response_xml'))
        self.assertTrue(type(query.soap_response_xml) is etree._Element)

        self.assertTrue(query.modified() > query.created())

        modifiedBefore = query.modified()
        lsfConnector.get()
        self.assertEqual(modifiedBefore, query.modified())

    def test_lsf_query_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.portal,
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
        self.assertTrue(
            fti.global_allow,
            u'{0} is not globally addable!'.format(fti.id)
        )
