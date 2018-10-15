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

    def test_update_all_view_is_registered(self):
        view = getMultiAdapter(
            (self.portal['other-folder'], self.portal.REQUEST),
            name='update-all-view'
        )
        self.assertTrue(view(), 'update-all-view is not found')
        self.assertTrue(
            'Sample View' in view(),
            'Sample View is not found in update-all-view'
        )
        self.assertTrue(
            'Sample View' in view(),
            'A small message is not found in update-all-view'
        )

    def test_update_all_view_in_my_collection(self):
        with self.assertRaises(ComponentLookupError):
            getMultiAdapter(
                (self.portal['my-collection'], self.portal.REQUEST),
                name='update-all-view'
            )


class ViewsFunctionalTest(unittest.TestCase):

    layer = UNIKOLD_CONNECTOR_FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
