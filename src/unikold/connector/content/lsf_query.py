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
        required=True
    )


@implementer(ILSFQuery)
class LSFQuery(SOAPQuery):

    def getSOAPResponse(self, wsdlUrl, wsdlMethod, wsdlMethodParameter):
        if self.use_authentication:
            username = api.portal.get_registry_record('unikold_connector_lsf.lsf_auth_username')
            password = api.portal.get_registry_record('unikold_connector_lsf.lsf_auth_password')

            if username is not None and password is not None:
                # add <user-auth> element for LSF authentication
                root = etree.fromstring(self.wsdl_method_parameter)
                userAuth = etree.SubElement(root, 'user-auth')
                elUser = etree.SubElement(userAuth, 'username')
                elUser.text = username
                elPW = etree.SubElement(userAuth, 'password')
                elPW.text = password
                wsdlMethodParameter = etree.tostring(root)

        # responses from LSF have a certain structure
        # here we remove useless stuff and store response additionally
        # as XML etree
        (data, error) = super(LSFQuery, self).getSOAPResponse(
            wsdlUrl, wsdlMethod, wsdlMethodParameter
        )
        if error is False:
            val = data['_value_1'].encode('utf-8')

            if 'error' in val:
                error = val
            else:
                data = etree.fromstring(val)
                self.soap_response_xml = data
                data = etree.tostring(data)

        return (data, error)
