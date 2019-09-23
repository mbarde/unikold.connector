# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from unikold.connector.content.ldap_search_query import ILDAPSearchQuery  # NOQA E501
from unikold.connector.testing import UNIKOLD_CONNECTOR_INTEGRATION_TESTING  # noqa
from unikold.connector.tests.config import ldap_search_password
from unikold.connector.tests.config import ldap_search_username
from unikold.connector.tests.config import ldap_server_address
from unikold.connector.tests.config import ldap_server_base_dn
from unikold.connector.tests.config import ldap_server_port
from zope.component import createObject
from zope.component import queryUtility

import pickle
import unittest


try:
    from plone.dexterity.schema import portalTypeToSchemaName
except ImportError:
    # Plone < 5
    from plone.dexterity.utils import portalTypeToSchemaName  # noqa: F401


class LDAPSearchQueryIntegrationTest(unittest.TestCase):

    layer = UNIKOLD_CONNECTOR_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_ct_ldap_search_query_schema(self):
        fti = queryUtility(IDexterityFTI, name='LDAPSearchQuery')
        schema = fti.lookupSchema()
        self.assertEqual(ILDAPSearchQuery, schema)

    def test_ct_ldap_search_query_fti(self):
        fti = queryUtility(IDexterityFTI, name='LDAPSearchQuery')
        self.assertTrue(fti)

    def test_ct_ldap_search_query_factory(self):
        fti = queryUtility(IDexterityFTI, name='LDAPSearchQuery')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            ILDAPSearchQuery.providedBy(obj),
            u'ILDAPSearchQuery not provided by {0}!'.format(
                obj,
            ),
        )

    def test_ct_ldap_search_query_adding(self):
        folderPath = api.portal.get_registry_record('unikold_connector.soap_queries_folder')
        folder = self.portal.restrictedTraverse(str(folderPath))
        setRoles(self.portal, TEST_USER_ID, ['Authenticated'])

        obj = api.content.create(
            container=folder,
            type='LDAPSearchQuery',
            id='ldap_search_query',
            **{
                'address': ldap_server_address,
                'port': ldap_server_port,
                'username': ldap_search_username,
                'password': ldap_search_password,
                'base_dn': ldap_server_base_dn,
                'filter': 'mail=mbarde@uni-koblenz.de'
            }
        )
        self.assertEqual(obj.getResults(), [])

        data = obj.getData()
        self.assertTrue(len(data) > 0)
        self.assertEqual(data, obj.raw_response)
        self.assertFalse(obj.raw_error)

        resultsWithDNs = obj.getResults()
        self.assertEqual(len(resultsWithDNs), 1)
        self.assertEqual(resultsWithDNs, pickle.loads(obj.raw_response))

        results = obj.getResultsWithoutDNs()
        self.assertEqual(len(results), 1)

        obj.raw_response = u'faulty string'
        results = obj.getResults()
        self.assertEqual(results[0][0], u'pickle loads error')

        # empty results:
        obj.filter = u'hello=world'
        data = obj.getData(forceUpdate=True)
        self.assertEqual(pickle.loads(data), [])
        self.assertEqual(data, obj.raw_response)
        self.assertFalse(obj.raw_error)
        self.assertEqual(obj.getResults(), [])

    def test_ct_ldap_search_query_fail(self):
        folderPath = api.portal.get_registry_record('unikold_connector.soap_queries_folder')
        folder = self.portal.restrictedTraverse(str(folderPath))
        setRoles(self.portal, TEST_USER_ID, ['Authenticated'])

        obj = api.content.create(
            container=folder,
            type='LDAPSearchQuery',
            id='ldap_search_query',
            **{
                'address': 'not-existing-address',
                'port': ldap_server_port,
                'username': ldap_search_username,
                'password': ldap_search_password,
                'base_dn': ldap_server_base_dn,
                'filter': 'mail=mbarde@uni-koblenz.de'
            }
        )

        data = obj.getData()
        self.assertEqual(len(data), 0)
        self.assertTrue(len(obj.raw_error) > 0)
        self.assertEqual(obj.raw_response, None)
        self.assertEqual(obj.getResults(), [])

    def test_ct_ldap_search_query_globally_not_addable(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='LDAPSearchQuery')
        self.assertFalse(
            fti.global_allow,
            u'{0} is globally addable!'.format(fti.id)
        )

    def test_excluded_from_search(self):
        types_not_searched = api.portal.get_registry_record('plone.types_not_searched')
        self.assertTrue('LDAPSearchQuery' in types_not_searched)
