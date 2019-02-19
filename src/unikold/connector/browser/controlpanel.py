# -*- coding: utf-8 -*-
from plone import api
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.protect.interfaces import IDisableCSRFProtection
from plone.z3cform import layout
from unikold.connector import _
from unikold.connector.content.soap_query import ISOAPQuery
from z3c.form import button
from zope import schema
from zope.interface import alsoProvides
from zope.interface import Interface
from zope.publisher.browser import BrowserView

import logging


class IUniKoLdConnectorControlPanelView(Interface):

    soap_queries_folder = schema.TextLine(
        title=_(u'SOAP-Queries folder'),
        description=_(u'Folder where SOAP queries are stored and cached. Must be the path to an existing SOAPQueriesFolder.'),  # noqa: E501
        required=True,
    )

    soap_timeout = schema.Int(
        title=_(u'Default timeout for SOAP requests (in seconds)'),
        required=False,
        default=10
    )


class UniKoLdConnectorControlPanelForm(RegistryEditForm):
    schema = IUniKoLdConnectorControlPanelView
    schema_prefix = 'unikold_connector'
    label = u'Uni Ko Ld Connector Settings'

    @button.buttonAndHandler(_(u'Save'), name='save')
    def handleSave(self, action):
        errorMsg = False
        data, errors = self.extractData()

        if 'soap_queries_folder' in data:
            soapQueriesPath = data['soap_queries_folder']
            portal = api.portal.get()
            try:
                folder = portal.restrictedTraverse(str(soapQueriesPath))
                if folder.portal_type != 'SOAPQueriesFolder':
                    errorMsg = _(u'Item at this location is not a SOAPQueriesFolder!')
            except KeyError:
                errorMsg = _(u'SOAPQueriesFolder does not exist at this location!')

            if errorMsg:
                api.portal.show_message(errorMsg, request=self.request, type='error')

        if errors or errorMsg:
            self.status = self.formErrorsMessage
            return

        self.applyChanges(data)
        api.portal.show_message(
            message=_(u'Changes saved.'),
            request=self.request, type='info')
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
                logging.error(
                    '[Connector] Could not update: {0} ({1})'.format(obj.id, str(obj))
                )
                updateError.append(obj)

        if len(updateSuccess) > 0:
            api.portal.show_message(
                message=_(u'Successfully updated ${successCount} queries',
                          mapping={u'successCount': len(updateSuccess)}),
                request=self.request, type='info')
        if len(updateError) > 0:
            api.portal.show_message(
                message=_(u'Error updating ${errorCount} queries (see logs for more information)',
                          mapping={u'errorCount': len(updateError)}),
                request=self.request, type='error')

    @button.buttonAndHandler(_(u'Count queries'))
    def handleCount(self, action):
        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog(object_provides=ISOAPQuery.__identifier__)
        api.portal.show_message(
            message=_(u'There are ${successCount} queries',
                      mapping={u'successCount': len(brains)}),
            request=self.request, type='info')

    @button.buttonAndHandler(_(u'Cancel'), name='cancel')
    def handleCancel(self, action):
        api.portal.show_message(
            message=_(u'Changes canceled.'),
            request=self.request, type='info')
        self.request.response.redirect(u'{0}/{1}'.format(
            api.portal.get().absolute_url(),
            self.control_panel_view
        ))


UniKoLdConnectorControlPanelView = layout.wrap_form(
    UniKoLdConnectorControlPanelForm, ControlPanelFormWrapper)


class Tasks(BrowserView):

    # can be used as async task as described in Readme
    def updateAllQueries(self):
        # make sure CSRF protection does not strike when request is called
        # via Zope clock server
        alsoProvides(self.request, IDisableCSRFProtection)

        logging.info('[Connector] Start updating all queries ...')
        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog(object_provides=ISOAPQuery.__identifier__)

        brainCount = len(brains)
        logging.info('[Connector] Found {0} queries to update ...'.format(str(brainCount)))

        updateSuccessCounter = 0
        updateErrorCounter = 0
        for brain in brains:
            obj = brain.getObject()
            if obj.updateData() is not False:
                updateSuccessCounter += 1
            else:
                logging.error(
                    '[Connector] Could not update: {0} ({1})'.format(obj.id, str(obj))
                )
                updateErrorCounter += 1

        logging.info(
            '[Connector] Updated successfully {0} of {1} queries!'
            .format(str(updateSuccessCounter), str(brainCount))
        )
