# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from unikold.connector.interfaces import IConnectedObject
from plone import api


class UpdateAllView(BrowserView):
    template = ViewPageTemplateFile('update_all_view.pt')

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        catalog = api.portal.get_tool('portal_catalog')
        brains = catalog(object_provides=IConnectedObject.__identifier__)

        self.updateSuccess = []
        self.updateError = []
        for brain in brains:
            obj = brain.getObject()
            if obj.updateFromConnection():
                self.updateSuccess.append(obj)
            else:
                self.updateError.append(obj)
        return self.template()
