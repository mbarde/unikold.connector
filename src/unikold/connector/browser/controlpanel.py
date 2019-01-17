# -*- coding: utf-8 -*-
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.z3cform import layout
from z3c.form import button
from zope import schema
from zope.interface import Interface
from unikold.connector.content.soap_query import ISOAPQuery
from Products.statusmessages.interfaces import IStatusMessage
from plone import api
from zope.component.hooks import getSite
from unikold.connector import _


class IUniKoLdConnectorControlPanelView(Interface):

    soap_queries_folder = schema.TextLine(
        title=_(u'SOAP-Queries folder'),
        description=_(u'Folder where SOAP queries are stored and cached'),
        required=False,
    )


class UniKoLdConnectorControlPanelForm(RegistryEditForm):
    schema = IUniKoLdConnectorControlPanelView
    schema_prefix = 'unikold_connector'
    label = u'Uni Ko Ld Connector Settings'

    @button.buttonAndHandler(_(u"Save"), name='save')
    def handleSave(self, action):
        data, errors = self.extractData()
        if errors:
            self.status = self.formErrorsMessage
            return
        self.applyChanges(data)
        IStatusMessage(self.request).addStatusMessage(
            _(u"Changes saved."),
            "info")
        self.request.response.redirect(self.request.getURL())

    @button.buttonAndHandler(_(u'Update all queries'))
    def handleUpdateAll(self, action):
        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog(object_provides=ISOAPQuery.__identifier__)

        updateSuccess = []
        updateError = []
        for brain in brains:
            obj = brain.getObject()
            if obj.updateData() is not False:
                updateSuccess.append(obj)
            else:
                print(
                    '[Connector] Could not update: {} ({})'.format(obj.id, str(obj))
                )
                updateError.append(obj)

        if len(updateSuccess) > 0:
            IStatusMessage(self.request).addStatusMessage(
                _(u'Successfully updated ${successCount} queries',
                    mapping={u'successCount': len(updateSuccess)}),
                'info')
        if len(updateError) > 0:
            IStatusMessage(self.request).addStatusMessage(
                _(u'Error updating ${errorCount} queries (see logs for more information)',  # NOQA
                    mapping={u'errorCount': len(updateError)}),
                'error')

    @button.buttonAndHandler(_(u'Count queries'))
    def handleCount(self, action):
        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog(object_provides=ISOAPQuery.__identifier__)
        IStatusMessage(self.request).addStatusMessage(
            _(u'There are ${successCount} queries',
                mapping={u'successCount': len(brains)}),
            'info')

    @button.buttonAndHandler(_(u"Cancel"), name='cancel')
    def handleCancel(self, action):
        IStatusMessage(self.request).addStatusMessage(
            _(u"Changes canceled."),
            "info")
        self.request.response.redirect(u"{0}/{1}".format(
            getSite().absolute_url(),
            self.control_panel_view
        ))


UniKoLdConnectorControlPanelView = layout.wrap_form(
    UniKoLdConnectorControlPanelForm, ControlPanelFormWrapper)
