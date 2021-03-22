# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from plone.i18n.normalizer import idnormalizer
from unikold.connector.content.ldap_search_query import ILDAPSearchQuery  # NOQA E501
from unikold.connector.ldap import LDAPSearchConnector
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
                'filter': 'mail=mbarde@uni-koblenz.de',
            }  # noqa: C815
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
                'filter': 'mail=mbarde@uni-koblenz.de',
            }  # noqa: C815
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
            u'{0} is globally addable!'.format(fti.id),
        )

    def test_excluded_from_search(self):
        types_not_searched = api.portal.get_registry_record('plone.types_not_searched')
        self.assertTrue('LDAPSearchQuery' in types_not_searched)

    def test_ldap_search_connecotr(self):
        searchFilter = 'mail=mbarde@uni-koblenz.de'
        ldapConnector = LDAPSearchConnector(
            ldap_server_address, ldap_server_port, ldap_server_base_dn,
            searchFilter, ldap_search_username, ldap_search_password,
            1,
        )

        query = ldapConnector.getQuery()
        self.assertEqual(query.raw_response, None)

        address = query.address
        self.assertEqual(address, ldap_server_address)

        queryResults = query.getResults()
        self.assertEqual(len(queryResults), 0)

        connectorResults = ldapConnector.get()

        queryResults = query.getResults()
        self.assertTrue(len(queryResults) > 0)
        self.assertEqual(str(type(queryResults)), "<class 'list'>")
        self.assertEqual(queryResults, connectorResults)

        self.assertTrue(query.modified() > query.created())

        modifiedBefore = query.modified()
        ldapConnector.get()
        self.assertEqual(modifiedBefore, query.modified())

        ldapConnector.get(forceUpdate=True)
        self.assertTrue(modifiedBefore < query.modified())

        # ensure correct path is created by connector to store query:
        containerPath = api.portal.get_registry_record('unikold_connector.soap_queries_folder')
        parts = containerPath.split('/')
        parts += ldap_server_address.split('/')
        parts += ldap_server_base_dn.split(',')
        parts += searchFilter.split('=')

        expectedPath = []
        for part in parts:
            if len(part) == 0:
                continue
            expectedPath.append(idnormalizer.normalize(part))

        queryPath = list(query.getPhysicalPath())[1:]
        self.assertEqual(queryPath, expectedPath)

    def test_ct_ldap_search_query_defaults(self):
        searchFilter = 'mail=mbarde@uni-koblenz.de'
        ldapConnector = LDAPSearchConnector(searchFilter=searchFilter)

        results = ldapConnector.get()
        self.assertTrue(len(results) > 0)
        self.assertEqual(str(type(results)), "<class 'list'>")

        query = ldapConnector.getQuery()
        address = query.address
        self.assertEqual(address, None)

        # ensure correct path is created by connector to store query:
        containerPath = api.portal.get_registry_record('unikold_connector.soap_queries_folder')
        parts = containerPath.split('/')
        parts += ldap_server_address.split('/')
        parts += ldap_server_base_dn.split(',')
        parts += searchFilter.split('=')

        expectedPath = []
        for part in parts:
            if len(part) == 0:
                continue
            expectedPath.append(idnormalizer.normalize(part))

        queryPath = list(query.getPhysicalPath())[1:]
        self.assertEqual(queryPath, expectedPath)

        ldapConnector = LDAPSearchConnector(searchFilter=searchFilter, address='')
        results = ldapConnector.get()
        self.assertTrue(len(results) > 0)
        self.assertEqual(str(type(results)), "<class 'list'>")

    def test_ct_ldap_search_query_overwrite_defaults(self):
        searchFilter = 'mail=mbarde@uni-koblenz.de'
        ldapConnector = LDAPSearchConnector(
            address='notexisting', searchFilter=searchFilter)

        data = ldapConnector.get()
        self.assertEqual(len(data), 0)

        query = ldapConnector.getQuery()
        self.assertTrue(len(query.raw_error) > 0)
        self.assertEqual(query.raw_response, None)
        self.assertEqual(query.getResults(), [])
