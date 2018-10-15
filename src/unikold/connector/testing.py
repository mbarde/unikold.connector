# -*- coding: utf-8 -*-
from plone.app.contenttypes.testing import PLONE_APP_CONTENTTYPES_FIXTURE
from plone.app.robotframework.testing import REMOTE_LIBRARY_BUNDLE_FIXTURE
from plone.app.testing import applyProfile
from plone.app.testing import FunctionalTesting
from plone.app.testing import IntegrationTesting
from plone.app.testing import PloneSandboxLayer
from plone.testing import z2

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
