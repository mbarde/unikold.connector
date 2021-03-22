# -*- coding: utf-8 -*-
from plone import api
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.dexterity.interfaces import IDexterityFTI
from plone.testing import z2
from unikold.connector.tests.config import ldap_search_password
from unikold.connector.tests.config import ldap_search_username
from unikold.connector.tests.config import ldap_server_address
from unikold.connector.tests.config import ldap_server_base_dn
from unikold.connector.tests.config import ldap_server_port
from unikold.connector.tests.config import lsf_auth_password
from unikold.connector.tests.config import lsf_auth_username
from unikold.connector.tests.config import lsf_wsdl_search_url
from unikold.connector.tests.config import lsf_wsdl_url
from zope.component import queryUtility

import unikold.connector


class UnikoldConnectorLayer(PloneSandboxLayer):

    defaultBases = (PLONE_APP_CONTENTTYPES_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load any other ZCML that is required for your tests.
        # The z3c.autoinclude feature is disabled in the Plone fixture base
        # layer.
        self.loadZCML(package=unikold.connector)

    def setUpPloneSite(self, portal):
        applyProfile(portal, 'unikold.connector:default')

        self.setUpDataFolder(portal)
        self.setUpLSFControlpanel()
        self.setUpLDAPControlpanel()

    def setUpDataFolder(self, portal):
        dataFolderName = 'soap-data'
        root = api.portal.get_navigation_root(portal)

        # temporary allow adding of SOAPQueriesFolder at root
        fti = queryUtility(IDexterityFTI, name='SOAPQueriesFolder')
        fti.global_allow = True

        folder = api.content.create(
            type='SOAPQueriesFolder',
            title=dataFolderName,
            id=dataFolderName,
            container=root)

        fti.global_allow = False

        path = '/'.join(folder.getPhysicalPath())
        api.portal.set_registry_record('unikold_connector.soap_queries_folder', path)
        api.portal.set_registry_record('unikold_connector.soap_timeout', 10)

    def setUpLSFControlpanel(self):
        api.portal.set_registry_record('unikold_connector_lsf.lsf_wsdl_url', lsf_wsdl_url)
        api.portal.set_registry_record('unikold_connector_lsf.lsf_wsdl_search_url', lsf_wsdl_search_url)  # noqa: E501
        api.portal.set_registry_record('unikold_connector_lsf.lsf_auth_username', lsf_auth_username)  # noqa: E501
        api.portal.set_registry_record('unikold_connector_lsf.lsf_auth_password', lsf_auth_password)  # noqa: E501

    def setUpLDAPControlpanel(self):
        api.portal.set_registry_record('unikold_connector_ldap.ldap_default_address', ldap_server_address)  # noqa: E501
        api.portal.set_registry_record('unikold_connector_ldap.ldap_default_port', ldap_server_port)  # noqa: E501
        api.portal.set_registry_record('unikold_connector_ldap.ldap_default_username', ldap_search_username)  # noqa: E501
        api.portal.set_registry_record('unikold_connector_ldap.ldap_default_password', ldap_search_password)  # noqa: E501
        api.portal.set_registry_record('unikold_connector_ldap.ldap_default_base_dn', ldap_server_base_dn)  # noqa: E501


UNIKOLD_CONNECTOR_FIXTURE = UnikoldConnectorLayer()


UNIKOLD_CONNECTOR_INTEGRATION_TESTING = IntegrationTesting(
    bases=(UNIKOLD_CONNECTOR_FIXTURE,),
    name='UnikoldConnectorLayer:IntegrationTesting',
)


UNIKOLD_CONNECTOR_FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(UNIKOLD_CONNECTOR_FIXTURE,),
    name='UnikoldConnectorLayer:FunctionalTesting',
)


UNIKOLD_CONNECTOR_ACCEPTANCE_TESTING = FunctionalTesting(
    bases=(
        UNIKOLD_CONNECTOR_FIXTURE,
        REMOTE_LIBRARY_BUNDLE_FIXTURE,
        z2.ZSERVER_FIXTURE,
    ),
    name='UnikoldConnectorLayer:AcceptanceTesting',
)
