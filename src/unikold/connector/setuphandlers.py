# -*- coding: utf-8 -*-
from plone import api
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer


@implementer(INonInstallable)
class HiddenProfiles(object):

    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            'unikold.connector:uninstall',
        ]


def makeTypeSearchable(portal, type_id, searchable):
    blacklisted = list(api.portal.get_registry_record('plone.types_not_searched'))
    if searchable and type_id in blacklisted:
        blacklisted.remove(type_id)
    elif not searchable and type_id not in blacklisted:
        blacklisted.append(type_id)
    api.portal.set_registry_record('plone.types_not_searched', tuple(blacklisted))


def post_install(context):
    portal = api.portal.get()
    makeTypeSearchable(portal, 'SOAPQuery', searchable=False)
    makeTypeSearchable(portal, 'LSFQuery', searchable=False)
    makeTypeSearchable(portal, 'LSFSearchQuery', searchable=False)
    makeTypeSearchable(portal, 'XMLQuery', searchable=False)
    makeTypeSearchable(portal, 'SOAPQueriesFolder', searchable=False)
    makeTypeSearchable(portal, 'LDAPSearchQuery', searchable=False)


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.
