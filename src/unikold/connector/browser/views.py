# -*- coding: utf-8 -*-
from Products.Five.browser import BrowserView
from zeep import Client
from lxml import etree
from plone.dexterity.browser.view import DefaultView
from zope.security import checkPermission
from unikold.connector.soap import SOAPConnector
# keep in mind: https://github.com/mvantellingen/python-zeep/pull/657/commits/a2b7ec0296bcb0ac47a5d15669dcb769447820eb  # NOQA: E501


class SOAPTestView(BrowserView):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        self.soapRequestAsString = False
        self.soapError = False
        self.soapResult = False

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

            self.soapRequestAsString = soapStr
            (data, err) = self.getXMLData(wsdlUrl, wsdlMethod, soapStr)
            if err:
                self.soapError = err
            else:
                self.soapResult = etree.tostring(data)

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
            username = ''
            password = ''
            userAuth = etree.SubElement(root, 'user-auth')
            elUser = etree.SubElement(userAuth, 'username')
            elUser.text = username
            elPW = etree.SubElement(userAuth, 'password')
            elPW.text = password

        return etree.tostring(root, pretty_print=True)

    def getXMLData(self, wsdlUrl, wsdlMethod, xmlStr):
        data = False
        error = False

        try:
            client = Client(wsdlUrl)
            # dynamically call wsdl method like 'getXMLData'
            res = getattr(client.service, wsdlMethod)(xmlStr)
            val = res['_value_1'].encode('utf-8')

            if 'error' in val:
                error = val
            else:
                data = etree.fromstring(val)
        except Exception as exc:
            error = str(exc) + '\n\nRaw answer:\n' + val
        finally:
            return (data, error)

    def inputParametersToList(self, text):
        result = []
        rows = [u.strip() for u in text.split('\r\n') if len(u.strip()) > 0]
        for row in rows:
            splitted = row.split(':')
            if len(splitted) == 2:
                result.append((splitted[0], splitted[1]))
        return result

    def testSOAPQuery(self):
        soapConnector = SOAPConnector(
            'https://klips.uni-koblenz.de/qisserver/services/soapsearch?WSDL',
            'search',
            '<search><object>einrichtung</object><expression></expression></search>',
            24
        )
        data = soapConnector.get()
        import pdb; pdb.set_trace()


class SOAPQueryView(DefaultView):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        updateSoap = self.request.form.get('updateSOAP', False)
        if updateSoap:
            self.context.updateData()
        return super(SOAPQueryView, self).__call__()

    def canModify(self):
        return checkPermission('cmf.ModifyPortalContent', self.context)
