# -*- coding: utf-8 -*-
from datetime import datetime
from datetime import timedelta
from plone import api
from plone.app.registry.browser.controlpanel import ControlPanelFormWrapper
from plone.app.registry.browser.controlpanel import RegistryEditForm
from plone.protect.interfaces import IDisableCSRFProtection
from plone.z3cform import layout
from unikold.connector import _
from unikold.connector.interfaces import IUniKoLdQuery
from z3c.form import button
from zope import schema
from zope.interface import alsoProvides
from zope.interface import Interface
from zope.publisher.browser import BrowserView

import logging
import pytz


class IUniKoLdConnectorControlPanelView(Interface):

    soap_queries_folder = schema.TextLine(
        title=_(u'SOAP-Queries folder'),
        description=_(u'Folder where SOAP queries are stored and cached. Must be the path to an existing SOAPQueriesFolder.'),  # noqa: E501
        required=True,
    )

    soap_timeout = schema.Int(
        title=_(u'Default timeout for SOAP requests (in seconds)'),
        required=False,
        default=10,
    )

    lifetime_queries = schema.Int(
        title=_(u'Lifetime of queries (in days)'),
        description=_(u'Queries which have not been modified since X days will be removed (when calling `unikold.connector.cleanup`)'),  # noqa: E501
        required=True,
        default=365,
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
        brains = catalog(object_provides=IUniKoLdQuery.__identifier__)

        updateSuccess = []
        updateIgnored = []
        updateError = []
        for brain in brains:
            obj = brain.getObject()
            if obj.exclude_from_auto_update:
                updateIgnored.append(obj)
                continue
            if obj.updateData() is not False:
                updateSuccess.append(obj)
            else:
                logging.error(
                    '[Connector] Could not update: {0} ({1})'.format(
                        obj.id, '/'.join(obj.getPhysicalPath())),
                )
                updateError.append(obj)

        if len(updateSuccess) > 0:
            api.portal.show_message(
                message=_(u'Successfully updated ${successCount} queries',
                          mapping={u'successCount': len(updateSuccess)}),
                request=self.request, type='info')
        if len(updateIgnored) > 0:
            api.portal.show_message(
                message=_(u'Ignored ${ingoredCount} queries (are excluded from automated updates)',
                          mapping={u'ingoredCount': len(updateIgnored)}),
                request=self.request, type='warning')
        if len(updateError) > 0:
            api.portal.show_message(
                message=_(u'Error updating ${errorCount} queries (see logs for more information)',
                          mapping={u'errorCount': len(updateError)}),
                request=self.request, type='error')

    @button.buttonAndHandler(_(u'Count queries'))
    def handleCount(self, action):
        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog(object_provides=IUniKoLdQuery.__identifier__)
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
            self.control_panel_view,
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
        brains = catalog(object_provides=IUniKoLdQuery.__identifier__)

        brainCount = len(brains)
        logging.info('[Connector] Found {0} queries to update ...'.format(str(brainCount)))

        updateSuccessCounter = 0
        updateErrorCounter = 0
        for brain in brains:
            obj = brain.getObject()
            if obj.exclude_from_auto_update:
                continue
            if obj.updateData() is not False:
                updateSuccessCounter += 1
            else:
                logging.error(
                    '[Connector] Could not update: {0} ({1})'.format(
                        obj.id, '/'.join(obj.getPhysicalPath())),
                )
                updateErrorCounter += 1

        logging.info(
            '[Connector] Updated successfully {0} of {1} queries!'
            .format(str(updateSuccessCounter), str(brainCount)),
        )

    def removeStaleQueries(self):
        alsoProvides(self.request, IDisableCSRFProtection)

        daysLifetime = api.portal.get_registry_record('unikold_connector.lifetime_queries')
        now = datetime.now()
        compareDate = now - timedelta(days=daysLifetime)
        # make offset aware (not naive)
        compareDate = pytz.UTC.localize(compareDate)

        logging.info('[Connector] Looking for stale queries (last modifed {0} days ago)...'
                     .format(daysLifetime))
        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog(object_provides=IUniKoLdQuery.__identifier__)

        toRemove = []
        for brain in brains:
            if brain.modified.asdatetime() <= compareDate:
                toRemove.append(brain.getObject())

        logging.info('[Connector] Found {0} stale queries. Removing ...'
                     .format(str(len(toRemove))))

        api.content.delete(objects=toRemove)

        logging.info('[Connector] Successfully removed {0} stale queries.'
                     .format(str(len(toRemove))))
