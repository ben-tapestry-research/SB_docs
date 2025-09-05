import xml.etree.ElementTree as ET
from typing import Iterable


def _attr(el: ET, name: str, default="") -> str:
    """ Returns the value of a given attribute from an ElementTree

    Args:
        el (ET): The ElementTree object to search
        name (str): The name of the attribute to fetch
    Returns:
        str: The value of the attribute, or None if it does not exist
    """
    return el.attrib.get(name, default)


def _bit(el: ET, attr_name: str):  # returns bool | None
    """Helper function to return a boolean based upon attribute value
        e.g. randomize="0" --> False
             randomize="1" --> True

    Args:
        el (ET): The ElementTree object to work with
        attr_name (str): The name of the attribute to fetch (e.g. "randomize")

    Returns:
        bool | None: Boolean value or None
    """
    v = _attr(el, attr_name, None)
    if v is None:
        return None
    # Interpret as boolean
    return str(v).strip().lower() in {"1"}


def _tag_text(el: ET, tag: str) -> str:
    """Returns the text within a given tag, or None if the tag does not exist or has no text.

    Args:
        el (ET): The ElementTree object to search
        tag (str): The tag to search for

    Returns:
        str: The text within the tag, or None if the tag does not exist or has no text.
    """
    node = el.find(tag)
    return node.text if (node is not None and node.text is not None) else None


def _append_children(parent: ET.Element, children) -> None:
    """ 
    Append child elements to a parent XML element. Used in Question.to_xml_element() to add rows, cols, and choices.
        Args:
            parent (ET.Element): The parent XML element to which children will be appended.
            children (iterable): An iterable of child elements to append.
    """
    if not children:
        return
    for child in children:
        parent.append(child.to_xml_element())


def to_xml_string(el: ET.Element, pretty: bool = False) -> str:
    """ 
    Converts an ElementTree element back into an XML string
    Args:
        el (ET.Element): The ElementTree element to convert
        pretty (bool, optional): Whether to pretty-print the XML. Defaults to False.
        Returns:
        str: The XML string
    """
    xml_string = ET.tostring(el, encoding="unicode")
    if not pretty:
        return xml_string
    try:
        from xml.dom import minidom
        return minidom.parseString(xml_string).toprettyxml(indent="  ")
    except Exception:
        return xml_string
