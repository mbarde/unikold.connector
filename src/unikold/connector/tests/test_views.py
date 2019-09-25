# -*- coding: utf-8 -*-
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from unikold.connector.content.lsf_search_query import ILSFSearchQuery  # NOQA E501
from unikold.connector.testing import UNIKOLD_CONNECTOR_INTEGRATION_TESTING  # noqa

import unittest


try:
    from plone.dexterity.schema import portalTypeToSchemaName
except ImportError:
    # Plone < 5
    from plone.dexterity.utils import portalTypeToSchemaName  # noqa: F401


class ViewsIntegrationTest(unittest.TestCase):

    layer = UNIKOLD_CONNECTOR_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_controlpanels(self):
        html = self.getObjectViewHTML(obj=self.portal, view='@@unikold-connector-controlpanel')
        self.assertTrue('Connector Settings' in html)
        html = self.getObjectViewHTML(obj=self.portal, view='@@unikold-connector-lsf-controlpanel')
        self.assertTrue('Connector LSF Settings' in html)
        html = self.getObjectViewHTML(obj=self.portal, view='@@unikold-connector-ldap-controlpanel')
        self.assertTrue('Connector LDAP Settings' in html)

    def getObjectViewHTML(self, obj, view='view'):
        viewPath = '/'.join(obj.getPhysicalPath()) + '/' + view
        view = self.portal.restrictedTraverse(viewPath)
        return view()
