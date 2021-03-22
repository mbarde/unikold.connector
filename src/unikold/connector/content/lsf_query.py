# -*- coding: utf-8 -*-
from lxml import etree
from plone import api
from unikold.connector import _
from unikold.connector.content.soap_query import ISOAPQuery
from unikold.connector.content.soap_query import SOAPQuery
from unikold.connector.utils_sentry import sentry_message
from zope import schema
from zope.interface import implementer


class ILSFQuery(ISOAPQuery):

    use_authentication = schema.Bool(
        title=_(u'Use LSF authentication'),
        description=_(u'Credentials have to be set in the controlpanel'),
        required=False,
    )

    lsf_response = schema.Text(
        title=_(u'LSF response'),
        description=_(u'LSF response extracted from the SOAP response'),
        required=False,
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
            wsdlMethodParameter=wsdlMethodParameter,
        )
        if error is False:
            valueyKey = '_value_1'
            if getattr(data, valueyKey, None) is None:
                error = 'Invalid LSF SOAP response: ' + str(data)
                return (data, error)

            data = data['_value_1']
            if 'error' in data:
                error = data
                sentry_message('Error in LSF SOAP response of {0}: {1}'
                               .format(self.absolute_url(), error))
            else:
                self.lsf_response = data
        else:
            sentry_message('Error in LSF SOAP response of {0}')

        return (data, error)

    def getLSFResponse(self):
        response = getattr(self, 'lsf_response', None)
        if response is not None:
            try:
                if not isinstance(response, bytes):
                    response = response.encode()
                tree = etree.fromstring(response)
            except (etree.XMLSyntaxError, ValueError):
                tree = etree.Element('xml-syntax-error')
                sentry_message('XML syntax error parsing lsf_response of {0}'
                               .format(self.absolute_url()))
            return tree
        return etree.Element('empty')
