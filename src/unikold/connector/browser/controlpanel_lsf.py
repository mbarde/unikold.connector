# -*- coding: utf-8 -*-
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.z3cform import layout
from unikold.connector import _
from zope import schema
from zope.interface import Interface


class IUniKoLdConnectorLSFControlPanelView(Interface):

    lsf_wsdl_url = schema.TextLine(
        title=_(u'LSF WSDL URL'),
        description=_(u'URL of the WSDL file of the LSF endpoint'),
        required=False,
    )

    lsf_wsdl_search_url = schema.TextLine(
        title=_(u'LSF-search WSDL URL'),
        description=_(u'URL of the WSDL file of the LSF search endpoint'),
        required=False,
    )

    lsf_auth_username = schema.TextLine(
        title=_(u'Username for LSF authentication'),
        description=_(u'Has to be specified in order to be able to use the authentication feature'),
        required=False,
    )

    lsf_auth_password = schema.Password(
        title=_(u'Password for LSF authentication'),
        description=_(u'Has to be specified in order to be able to use the authentication feature'),
        required=False,
    )


class UniKoLdConnectorLSFControlPanelForm(RegistryEditForm):
    schema = IUniKoLdConnectorLSFControlPanelView
    schema_prefix = 'unikold_connector_lsf'
    label = u'Connector LSF Settings'


UniKoLdConnectorLSFControlPanelView = layout.wrap_form(
    UniKoLdConnectorLSFControlPanelForm, ControlPanelFormWrapper)
