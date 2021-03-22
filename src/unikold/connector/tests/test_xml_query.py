# -*- coding: utf-8 -*-
from lxml import etree
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from plone.i18n.normalizer import idnormalizer
from unikold.connector.content.xml_query import IXMLQuery  # NOQA E501
from unikold.connector.testing import UNIKOLD_CONNECTOR_INTEGRATION_TESTING  # noqa
from unikold.connector.tests.config import xml_basic_auth_password
from unikold.connector.tests.config import xml_basic_auth_url
from unikold.connector.tests.config import xml_basic_auth_username
from unikold.connector.tests.config import xml_test_url
from unikold.connector.xml import XMLConnector
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
            **{
                'url': xml_test_url,
            }  # noqa: C815
        )

        data = obj.getData()
        self.assertTrue(len(data) > 0)
        self.assertEqual(data, obj.raw_response)
        self.assertFalse(obj.raw_error)

        xml = obj.getXMLResponse()
        self.assertTrue(type(xml) is etree._Element)
        self.assertTrue(len(xml) > 0)

        obj.url = 'definitelyNotAnUrl'
        obj.getData(True)  # force an update
        expectedError = "unknown url type: '{0}'".format(obj.url)
        self.assertEqual(obj.raw_error, expectedError)
        # since update failed stored response should not be updated
        self.assertEqual(obj.raw_response, data)

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
            u'{0} is globally addable!'.format(fti.id),
        )

    def test_excluded_from_search(self):
        types_not_searched = api.portal.get_registry_record('plone.types_not_searched')
        self.assertTrue('XMLQuery' in types_not_searched)

    def test_xml_query_connector(self):
        xmlConnector = XMLConnector(
            xml_test_url,
            24,
        )

        query = xmlConnector.getQuery()
        self.assertEqual(query.raw_response, None)

        xml = query.getXMLResponse()
        self.assertTrue(type(xml) is etree._Element)
        self.assertTrue(len(xml) == 0)

        data = xmlConnector.get()
        self.assertTrue(type(xml) is etree._Element)
        self.assertTrue(len(data) > 0)

        xml = query.getXMLResponse()
        self.assertTrue(type(xml) is etree._Element)
        self.assertTrue(len(xml) > 0)

        self.assertTrue(query.modified() > query.created())

        modifiedBefore = query.modified()
        xmlConnector.get()
        self.assertEqual(modifiedBefore, query.modified())

        xmlConnector.get(True)  # force update
        self.assertTrue(modifiedBefore < query.modified())

    def test_xml_query_connector_with_params(self):
        params = ['hello=world', 'möth=lämp']
        xmlConnector = XMLConnector(
            xml_test_url,
            24,
            params,
        )

        xml = xmlConnector.get()
        self.assertTrue(type(xml) is etree._Element)
        self.assertTrue(len(xml) > 0)

        queryPath = list(xmlConnector.getQuery().getPhysicalPath()[3:])

        expectedPath = []
        for part in xml_test_url.split('/'):
            if len(part) == 0:
                continue
            expectedPath.append(idnormalizer.normalize(part))
        for param in sorted(params):
            expectedPath.append(idnormalizer.normalize(param))
        expectedPath.append(xmlConnector.getQueryID())

        self.assertEqual(queryPath, expectedPath)

    def test_xml_query_with_auth(self):
        folderPath = api.portal.get_registry_record('unikold_connector.soap_queries_folder')
        folder = self.portal.restrictedTraverse(str(folderPath))
        setRoles(self.portal, TEST_USER_ID, ['Authenticated'])

        objNoAuth = api.content.create(
            container=folder, type='XMLQuery', id='xml_query_no_auth',
            **{'url': xml_basic_auth_url})
        data = objNoAuth.getData()
        self.assertEqual(data, '')
        self.assertTrue(len(objNoAuth.raw_error) > 0)

        obj = api.content.create(
            container=folder,
            type='XMLQuery',
            id='xml_query',
            **{
                'url': xml_basic_auth_url,
                'basic_auth_username': xml_basic_auth_username,
                'basic_auth_password': xml_basic_auth_password,
            }  # noqa: C815
        )

        data = obj.getData()
        self.assertTrue(len(data) > 0)
        self.assertEqual(data, obj.raw_response)
        self.assertFalse(obj.raw_error)

        xml = obj.getXMLResponse()
        self.assertTrue(type(xml) is etree._Element)
        self.assertTrue(len(xml) > 0)

    def test_xml_query_connector_with_auth(self):
        xmlConnector = XMLConnector(
            xml_basic_auth_url, 24,
            basicAuthCredentials=(xml_basic_auth_username, xml_basic_auth_password),
        )
        xml = xmlConnector.get()
        self.assertTrue(type(xml) is etree._Element)
        self.assertTrue(len(xml) > 0)
