# -*- coding: utf-8 -*-
from plone.dexterity.content import Item
from plone.supermodel import model
from zope.interface import implementer
from zope import schema
from lxml import etree
from unikold.connector.connectedObject import ConnectedObjectSOAP
from unikold.connector import _


class ITestType(model.Schema):
    """ Marker interface and Dexterity Python Schema for TestType
    """

    text = schema.Text(
        title=_(u'Text'),
        required=False
    )

    method_name = schema.TextLine(
        title=_(u'Methodname'),
        required=True
    )


@implementer(ITestType)
class TestType(Item, ConnectedObjectSOAP):
    wsdlUrl = 'https://klips.uni-koblenz.de/qisserver/services/dbinterface?WSDL'  # NOQA

    def updateFromConnection(self):
        (xml, error) = self.getXMLData(self.method_name)
        if error:
            return False
        self.text = str(etree.tostring(xml))
        return True
