import xml.etree.ElementTree as ET

from survey_elements.question_elements import *

def to_xml_string(el: ET.Element, pretty: bool = False) -> str:
    xml = ET.tostring(el, encoding="unicode")
    if not pretty:
        return xml
    try:
        from xml.dom import minidom
        return minidom.parseString(xml).toprettyxml(indent="  ")
    except Exception:
        return xml

xml = """
<radio label="Q1" cond="1">
  <title>How satisfied are you?</title>
  <row label="r1" cond="0">Very satisfied</row>
  <row label="r2">Somewhat satisfied</row>
</radio>
"""

root = ET.fromstring(xml)

root = ET.fromstring(xml)       # root.tag == "radio"
root.attrib                     # {"label": "Q1", "id": "q1"}
root.find("title").text         # "How satisfied are you?"
# [<Element 'row' at ...>, <Element 'row' at ...>]
root.findall("row")


def _attr(el: ET, name: str) -> str:
    """ Returns the value of a given attribute from an ElementTree

    Args:
        el (ET): The ElementTree object to search
        name (str): The name of the attribute to fetch
    Returns:
        str: The value of the attribute, or None if it does not exist
    """
    return el.attrib.get(name)


def _tag_text(el: ET, tag: str) -> str:
    """Returns the text within a given tag, or None if the tag does not exist or has no text.

    Args:
        el (ET): The ElementTree object to search
        tag (str): The tag to search for

    Returns:
        _type_: The text within the tag, or None if the tag does not exist or has no text.
    """
    node = el.find(tag)
    return node.text if (node is not None and node.text is not None) else None

# <row label="r1">Very satisfied</row>
def parse_row(row_el) -> Row:
    return Row(
        label=_attr(row_el, "label"),
        content=row_el.text,
        cond=_attr(row_el, "cond")
    )


my_row = parse_row(root.findall("row")[0])
print(my_row.cond)