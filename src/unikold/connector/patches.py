# -*- coding: utf-8 -*-
# flake8: noqa
# (ignore this file to be able to keep original code as original
#  as possible whilst working with own linter rules)
from lxml import etree
from zeep.xsd.const import NotSet, SkipValue, xsi_ns
from zeep.xsd.elements import Element
from zeep.xsd.types.complex import ComplexType
from zeep.xsd.valueobjects import ArrayValue, CompoundValue

import six
import typing


# apply fix
# https://github.com/mvantellingen/python-zeep/pull/657/commits/a2b7ec0296bcb0ac47a5d15669dcb769447820eb
def ComplexType_render(
        self,
        node: etree._Element,
        value: typing.Union[list, dict, CompoundValue],
        xsd_type: "ComplexType" = None,
        render_path=None,
) -> None:
    """Serialize the given value lxml.Element subelements on the node
    element.

    :param render_path: list

    """
    if not render_path:
        render_path = [self.name]

    if not self.elements_nested and not self.attributes:
        return

    # TODO: Implement test case for this
    if value is None:
        value = {}

    if isinstance(value, ArrayValue):
        value = value.as_value_object()

    # Render attributes
    for name, attribute in self.attributes:
        # apply fix
        # attr_value = value[name] if name in value else NotSet
        attr_value = value[name] if name in value and not isinstance(value, six.string_types) else NotSet  # noqa: E501
        child_path = render_path + [name]
        attribute.render(node, attr_value, child_path)

    if (
        len(self.elements_nested) == 1
        and isinstance(value, tuple(self.accepted_types))
        and not isinstance(value, (list, dict, CompoundValue))
    ):
        element = self.elements_nested[0][1]
        element.type.render(node, value, None, child_path)
        return

    # Render sub elements
    for name, element in self.elements_nested:
        if isinstance(element, Element) or element.accepts_multiple:
            # apply fix
            # element_value = value[name] if name in value else NotSet
            element_value = value[name] if name in value and not isinstance(value, six.string_types) else NotSet  # noqa: E501
            child_path = render_path + [name]
        else:
            element_value = value
            child_path = list(render_path)

        # We want to explicitly skip this sub-element
        if element_value is SkipValue:
            continue

        if isinstance(element, Element):
            element.type.render(node, element_value, None, child_path)
        else:
            element.render(node, element_value, child_path)

    if xsd_type:
        if xsd_type._xsd_name:
            node.set(xsi_ns("type"), xsd_type._xsd_name)
        if xsd_type.qname:
            node.set(xsi_ns("type"), xsd_type.qname)