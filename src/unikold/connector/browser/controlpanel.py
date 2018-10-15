# -*- coding: utf-8 -*-
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.z3cform import layout
from z3c.form import button
from zope.interface import Interface
from unikold.connector.interfaces import IConnectedObject
from Products.statusmessages.interfaces import IStatusMessage
from plone import api
from unikold.connector import _


class IUniKoLdConnectorControlPanelView(Interface):
    ''' Schema definition here '''


class UniKoLdConnectorControlPanelForm(RegistryEditForm):
    schema = IUniKoLdConnectorControlPanelView
    schema_prefix = 'unikoldconnector'
    label = u'Uni Ko Ld Connector Einstellungen'

    @button.buttonAndHandler(_(u'Update all connected objects'))
    def handleUpdateAll(self, action):
        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog(object_provides=IConnectedObject.__identifier__)

        updateSuccess = []
        updateError = []
        for brain in brains:
            obj = brain.getObject()
            if obj.updateFromConnection():
                updateSuccess.append(obj)
            else:
                print('[Connector] Could not update: ' + str(obj))
                updateError.append(obj)

        if len(updateSuccess) > 0:
            IStatusMessage(self.request).addStatusMessage(
                _(u'Successfully updated ${successCount} objects',
                    mapping={u'successCount': len(updateSuccess)}),
                'info')
        if len(updateError) > 0:
            IStatusMessage(self.request).addStatusMessage(
                _(u'Error updating ${errorCount} objects (see logs for more information)',  # NOQA
                    mapping={u'errorCount': len(updateError)}),
                'error')

    @button.buttonAndHandler(_(u'Count connected objects'))
    def handleCount(self, action):
        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog(object_provides=IConnectedObject.__identifier__)
        IStatusMessage(self.request).addStatusMessage(
            _(u'There are ${successCount} connected objects',
                mapping={u'successCount': len(brains)}),
            'info')

    @button.buttonAndHandler(_(u'Save'), name='save')
    def handleSave(self, action):
        super(UniKoLdConnectorControlPanelForm, self).handleSave(action)

    @button.buttonAndHandler(_(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        super(UniKoLdConnectorControlPanelForm, self).handleCancel(action)


UniKoLdConnectorControlPanelView = layout.wrap_form(
    UniKoLdConnectorControlPanelForm, ControlPanelFormWrapper)
