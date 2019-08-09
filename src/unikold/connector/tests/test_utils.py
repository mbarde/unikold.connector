# -*- coding: utf-8 -*-
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.i18n.normalizer import idnormalizer
from unikold.connector.testing import UNIKOLD_CONNECTOR_INTEGRATION_TESTING
from unikold.connector.utils import createNestedFolders

import unittest


try:
    from plone.dexterity.schema import portalTypeToSchemaName
except ImportError:
    # Plone < 5
    from plone.dexterity.utils import portalTypeToSchemaName  # noqa: F401


class ConnectorUtilsTest(unittest.TestCase):

    layer = UNIKOLD_CONNECTOR_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Authenticated'])

    def test_create_nested_folders(self):
        folderPath = api.portal.get_registry_record('unikold_connector.soap_queries_folder')
        container = self.portal.restrictedTraverse(str(folderPath))

        folderNames = ['https://', 'www.plone.org', '?key=value', 'stuff_',
                       ' ', '_____', '-dash-', '', '&%spec#+*', 'umläütöß']
        createNestedFolders(container, folderNames)

        # those folder names resolve to empty ids which means we expect
        # those will be skipped on nested folder creation
        nonExisting = [' ', '_____', '']

        currentFolder = container
        for folderName in folderNames:
            if folderName in nonExisting:
                continue
            folderId = idnormalizer.normalize(folderName)
            currentFolder = currentFolder.get(folderId, None)
            self.assertNotEqual(currentFolder, None)
