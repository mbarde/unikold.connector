# -*- coding: utf-8 -*-
from lxml import etree
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from unikold.connector.content.lsf_search_query import ILSFSearchQuery  # NOQA E501
from unikold.connector.lsf import LSFSearchConnector
from unikold.connector.testing import UNIKOLD_CONNECTOR_INTEGRATION_TESTING  # noqa
from unikold.connector.tests.config import lsf_auth_password
from unikold.connector.tests.config import lsf_auth_username
from unikold.connector.tests.config import lsf_wsdl_search_url
from zope.component import createObject
from zope.component import queryUtility

import unittest


try:
    from plone.dexterity.schema import portalTypeToSchemaName
except ImportError:
    # Plone < 5
    from plone.dexterity.utils import portalTypeToSchemaName  # noqa: F401


class LSFSearchQueryIntegrationTest(unittest.TestCase):

    layer = UNIKOLD_CONNECTOR_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        # set registry values user has to set via controlpanel
        registry = self.portal.portal_registry
        registry.records['unikold_connector_lsf.lsf_wsdl_search_url']._set_value(lsf_wsdl_search_url)  # noqa: E501
        registry.records['unikold_connector_lsf.lsf_auth_username']._set_value(lsf_auth_username)
        registry.records['unikold_connector_lsf.lsf_auth_password']._set_value(lsf_auth_password)

    def test_lsf_search_query_schema(self):
        fti = queryUtility(IDexterityFTI, name='LSFSearchQuery')
        schema = fti.lookupSchema()
        self.assertEqual(ILSFSearchQuery, schema)

    def test_lsf_search_query_fti(self):
        fti = queryUtility(IDexterityFTI, name='LSFSearchQuery')
        self.assertTrue(fti)

    def test_lsf_search_query_factory(self):
        fti = queryUtility(IDexterityFTI, name='LSFSearchQuery')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            ILSFSearchQuery.providedBy(obj),
            u'ILSFSearchQuery not provided by {0}!'.format(
                obj,
            ),
        )

    def test_lsf_search_query_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.portal,
            type='LSFSearchQuery',
            id='lsf_search_query',
        )

        self.assertTrue(
            ILSFSearchQuery.providedBy(obj),
            u'ILSFSearchQuery not provided by {0}!'.format(
                obj.id,
            ),
        )

    def test_lsf_search_query_connector(self):
        lsfSearchConnector = LSFSearchConnector(
            '<search><object>einrichtung</object><expression></expression></search>',  # noqa: E501
            24
        )

        query = lsfSearchConnector.getQuery()
        self.assertEqual(query.soap_response, None)
        self.assertFalse(hasattr(query, 'soap_response_xml'))
        self.assertFalse(hasattr(query, 'search_results'))

        data = lsfSearchConnector.get()
        self.assertTrue(len(data) > 0)
        self.assertTrue(type(data[0]) is dict)

        self.assertTrue(hasattr(query, 'soap_response_xml'))
        self.assertTrue(type(query.soap_response_xml) is etree._Element)

        self.assertTrue(hasattr(query, 'search_results'))
        self.assertTrue(type(query.search_results) is list)

        self.assertTrue(query.modified() > query.created())

        modifiedBefore = query.modified()
        lsfSearchConnector.get()
        self.assertEqual(modifiedBefore, query.modified())

    def test_lsf_search_query_globally_addable(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='LSFSearchQuery')
        self.assertTrue(
            fti.global_allow,
            u'{0} is not globally addable!'.format(fti.id)
        )
