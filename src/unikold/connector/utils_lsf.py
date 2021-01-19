# -*- coding: utf-8 -*-
from lxml import etree
from plone import api
from unikold.connector.content.lsf_query import LSFQuery


def buildLSFSOAPRequest(objectType, conditions=[]):
    root = etree.Element('SOAPDataService')
    general = etree.SubElement(root, 'general')
    object = etree.SubElement(general, 'object')
    object.text = objectType

    if len(conditions) > 0:
        condition = etree.SubElement(root, 'condition')
        for param in conditions:
            key = param[0]
            value = param[1]
            el = etree.SubElement(condition, key)
            el.text = value

    return etree.tostring(root, pretty_print=True)


def getLSFResponseNoCache(objectType, conditions, useAuthentication):
    query = LSFQuery()
    query.wsdl_url = api.portal.get_registry_record('unikold_connector_lsf.lsf_wsdl_url')
    query.wsdl_method = 'getDataXML'
    query.wsdl_method_parameter = buildLSFSOAPRequest(objectType, conditions)
    query.use_authentication = useAuthentication
    query.soap_response = None
    query.getData()
    return query.getLSFResponse()
