# -*- coding: utf-8 -*-
"""Module where all interfaces, events and exceptions live."""

from zope.interface import Interface
from zope.publisher.interfaces.browser import IDefaultBrowserLayer


class IUnikoldConnectorLayer(IDefaultBrowserLayer):
    """Marker interface that defines a browser layer."""


class IConnectedObject(Interface):
    """ Marker interface to query for connected objects """
    def updateFromConnection(self):
        pass
