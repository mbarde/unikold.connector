# -*- coding: utf-8 -*-
from lxml import etree
from plone import api
from unikold.connector import _
from unikold.connector.content.soap_query import ISOAPQuery
from unikold.connector.content.soap_query import SOAPQuery
from zope import schema
from zope.interface import implementer


class ILSFQuery(ISOAPQuery):

    use_authentication = schema.Bool(
        title=_(u'Use LSF authentication'),
        description=_(u'Credentials have to be set in the controlpanel'),
        required=False
    )

    lsf_response = schema.Text(
        title=_(u'LSF response'),
        description=_(u'LSF response extracted from the SOAP response'),
        required=False
    )


@implementer(ILSFQuery)
class LSFQuery(SOAPQuery):

    def getSOAPResponse(self):
        wsdlMethodParameter = self.wsdl_method_parameter

        if self.use_authentication:
            username = api.portal.get_registry_record('unikold_connector_lsf.lsf_auth_username')
            password = api.portal.get_registry_record('unikold_connector_lsf.lsf_auth_password')

            if username is not None and password is not None:
                # add <user-auth> element for LSF authentication
                try:
                    root = etree.fromstring(self.wsdl_method_parameter)
                    userAuth = etree.SubElement(root, 'user-auth')
                    elUser = etree.SubElement(userAuth, 'username')
                    elUser.text = username
                    elPW = etree.SubElement(userAuth, 'password')
                    elPW.text = password
                    wsdlMethodParameter = etree.tostring(root)
                except (etree.XMLSyntaxError, ValueError):
                    # if self.wsdl_method_parameter are not valid XML we can
                    # not add authentication - request will fail anyway
                    pass

        # responses from LSF have a certain structure
        # here we remove useless stuff and store LSF response additionally
        (data, error) = super(LSFQuery, self).getSOAPResponse(
            wsdlMethodParameter=wsdlMethodParameter
        )
        if error is False:
            valueyKey = '_value_1'
            if not hasattr(data, valueyKey):
                error = 'Invalid LSF SOAP response: ' + str(data)
                return (data, error)

            data = data['_value_1'].encode('utf-8')

            if 'error' in data:
                error = data
            else:
                self.lsf_response = data

        return (data, error)

    def getLSFResponse(self):
        if hasattr(self, 'lsf_response'):
            try:
                tree = etree.fromstring(self.lsf_response)
            except (etree.XMLSyntaxError, ValueError):
                tree = etree.Element('xml-syntax-error')
            return tree
        return etree.Element('empty')
