# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""
from zope.interface.interface import Attribute
from zope.interface.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IUnikoldConnectorLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IUniKoLdQuery(Interface):
    """Interface all query types of this addon have to implement"""

    lifetime = Attribute('lifetime')
    exclude_from_auto_update = Attribute('exclude_from_auto_update')

    def updateData():
        """ run query to update data """
