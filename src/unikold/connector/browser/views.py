# -*- coding: utf-8 -*-
from lxml import etree
from plone import api
from plone.dexterity.browser import add
from plone.dexterity.browser.view import DefaultView
from Products.Five.browser import BrowserView
from unikold.connector.utils import getSOAPResponse


class SOAPTestView(BrowserView):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        self.soapRequestAsString = False
        self.soapError = False
        self.soapResult = False

        isLSFRequest = self.request.form.get('isLSFRequest', False)
        wsdlUrl = self.request.form.get('wsdlUrl', False)
        wsdlMethod = self.request.form.get('wsdlMethod', False)
        method = self.request.form.get('method', False)
        parametersAsText = self.request.form.get('parameters', '')
        withAuth = self.request.form.get('useAuthentication', False)
        soapRequest = self.request.form.get('soapRequest', False)

        if wsdlUrl and wsdlMethod and (soapRequest or method):
            if soapRequest:
                soapStr = soapRequest
            else:
                parameters = self.inputParametersToList(parametersAsText)
                soapStr = self.buildSOAPRequest(method, parameters, withAuth)

            self.soapRequestAsString = self.coverPasswordInRequestStr(soapStr)
            (data, err) = getSOAPResponse(wsdlUrl, wsdlMethod, soapStr)
            if err:
                self.soapError = err
            else:
                if isLSFRequest:
                    val = getattr(data, '_value_1', False)
                    if val is False:
                        self.soapError = str(data)
                    else:
                        if 'error' in val:
                            self.soapError = val
                        else:
                            data = etree.fromstring(val)
                            data = etree.tostring(data)
                self.soapResult = data

        return self.index()

    def buildSOAPRequest(self, methodName, params=[], auth=False):
        root = etree.Element('SOAPDataService')
        general = etree.SubElement(root, 'general')
        object = etree.SubElement(general, 'object')
        object.text = methodName

        if len(params) > 0:
            condition = etree.SubElement(root, 'condition')
            for param in params:
                key = param[0]
                value = param[1]
                el = etree.SubElement(condition, key)
                el.text = value

        if auth:
            username = api.portal.get_registry_record('unikold_connector_lsf.lsf_auth_username')
            password = api.portal.get_registry_record('unikold_connector_lsf.lsf_auth_password')

            userAuth = etree.SubElement(root, 'user-auth')
            elUser = etree.SubElement(userAuth, 'username')
            elUser.text = username
            elPW = etree.SubElement(userAuth, 'password')
            elPW.text = password

        return etree.tostring(root, pretty_print=True)

    def inputParametersToList(self, text):
        result = []
        rows = [u.strip() for u in text.split('\r\n') if len(u.strip()) > 0]
        for row in rows:
            splitted = row.split(':')
            if len(splitted) == 2:
                result.append((splitted[0], splitted[1]))
        return result

    def coverPasswordInRequestStr(self, requestStr):
        startTag = '<password>'
        endTag = '</password>'

        if startTag not in requestStr or endTag not in requestStr:
            return requestStr

        idx0 = requestStr.index(startTag)
        idx1 = requestStr.index(endTag)
        pw = requestStr[idx0 + 10:idx1]
        return requestStr.replace(pw, '****')


class SOAPQueryView(DefaultView):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        updateSoap = self.request.form.get('update-request', False)
        if updateSoap and self.canUpdateFromView():
            self.context.updateData()
        return super(SOAPQueryView, self).__call__()

    def canUpdateFromView(self):
        return api.user.get_permissions(obj=self.context) \
            .get('Manage portal', False)

    def getModifiedLocalized(self):
        return api.portal.get_localized_time(self.context.modified(), long_format=True)


class DummyAddView(add.DefaultAddView):
    pass
