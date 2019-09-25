# -*- coding: utf-8 -*-
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.z3cform import layout
from unikold.connector import _
from zope import schema
from zope.interface import Interface


class IUniKoLdConnectorLDAPControlPanelView(Interface):

    ldap_default_address = schema.TextLine(
        title=_(u'Default LDAP server address'),
        default=u'',
        required=True,
    )

    ldap_default_port = schema.Int(
        title=_(u'Default LDAP server port'),
        default=389,
        required=True,
    )

    ldap_default_username = schema.TextLine(
        title=_(u'Default LDAP username'),
        default=u'',
        required=True,
    )

    ldap_default_password = schema.Password(
        title=_(u'Default LDAP password'),
        default=u'',
        required=True,
    )

    ldap_default_base_dn = schema.TextLine(
        title=_(u'Default base DN'),
        default=u'',
        required=True,
    )


class UniKoLdConnectorLDAPControlPanelForm(RegistryEditForm):
    schema = IUniKoLdConnectorLDAPControlPanelView
    schema_prefix = 'unikold_connector_ldap'
    label = u'Connector LDAP Settings'
    description = _(u'These defaults can be overwritten by LDAP search queries by setting values explicitly.')  # noqa: E501


UniKoLdConnectorLDAPControlPanelView = layout.wrap_form(
    UniKoLdConnectorLDAPControlPanelForm, ControlPanelFormWrapper)
