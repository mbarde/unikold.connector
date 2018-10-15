# -*- coding: utf-8 -*-
from unikold.connector.testing import UNIKOLD_CONNECTOR_FUNCTIONAL_TESTING
from unikold.connector.testing import UNIKOLD_CONNECTOR_INTEGRATION_TESTING
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from zope.component import getMultiAdapter
from zope.component.interfaces import ComponentLookupError

import unittest


class ViewsIntegrationTest(unittest.TestCase):

    layer = UNIKOLD_CONNECTOR_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        api.content.create(self.portal, 'Folder', 'other-folder')
        api.content.create(self.portal, 'Collection', 'my-collection')


class ViewsFunctionalTest(unittest.TestCase):

    layer = UNIKOLD_CONNECTOR_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
