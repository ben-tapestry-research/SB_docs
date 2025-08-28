import xml.etree.ElementTree as ET
from typing import List

from survey_elements.question_elements import *


def to_xml_string(el: ET.Element, pretty: bool = False) -> str:
    xml_string = ET.tostring(el, encoding="unicode")
    if not pretty:
        return xml_string
    try:
        from xml.dom import minidom
        return minidom.parseString(xml_string).toprettyxml(indent="  ")
    except Exception:
        return xml_string


xml = """
<radio label="Q1" cond="1">
  <title>How satisfied are you?</title>
  <row label="r1" cond="0" groups="g1">Very satisfied</row>
  <row label="r2">Somewhat satisfied</row>
</radio>
"""

root = ET.fromstring(xml)

root = ET.fromstring(xml)  # root.tag == "radio"
root.attrib  # {"label": "Q1", "id": "q1"}
root.find("title").text  # "How satisfied are you?"
# [<Element 'row' at ...>, <Element 'row' at ...>]
root.findall("row")

def _bit(el, name):  # returns bool | None
    v = _attr(el, name, None)
    if v is None: return None
    return str(v).strip().lower() in {"1", "true", "yes"}


def _attr(el: ET, name: str, default="") -> str:
    """ Returns the value of a given attribute from an ElementTree

    Args:
        el (ET): The ElementTree object to search
        name (str): The name of the attribute to fetch
    Returns:
        str: The value of the attribute, or None if it does not exist
    """
    return el.attrib.get(name, default)


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


# TODO: repetition in these - combine?
def parse_row(row_el) -> Row:
    return Row(
        label=_attr(row_el, "label"),
        content=row_el.text,
        cond=_attr(row_el, "cond"),
        alt=_attr(row_el, "alt"),
        randomize=_bit(row_el, "randomize"),
        groups=set(_attr(row_el, "groups").split(",")),
    )


def parse_rows(parent: ET.Element) -> tuple[Row, ...]:
    return tuple(parse_row(r) for r in parent.findall("row"))


def parse_col(col_el) -> Col:
    return Col(
        label=_attr(col_el, "label"),
        content=col_el.text,
        cond=_attr(col_el, "cond"),
        alt=_attr(col_el, "alt"),
        randomize=_bit(col_el, "randomize"),
        groups=set(_attr(col_el, "groups").split(",")),
    )


def parse_cols(parent: ET.Element) -> tuple[Col, ...]:
    return tuple(parse_col(r) for r in parent.findall("col"))


def parse_choice(choice_el) -> Choice:
    return Choice(
        label=_attr(choice_el, "label"),
        content=choice_el.text,
        cond=_attr(choice_el, "cond"),
        alt=_attr(choice_el, "alt"),
        randomize=_bit(choice_el, "randomize"),
        groups=set(_attr(choice_el, "groups").split(",")),
    )


def parse_choices(parent: ET.Element) -> tuple[Choice, ...]:
    return tuple(parse_choice(r) for r in parent.findall("choice"))


def parse_radio(radio_el) -> RadioQuestion:
    return RadioQuestion(
        # Mandatory
        label=_attr(radio_el, "label"),
        title=_tag_text(radio_el, "title"),
        rows=parse_rows(radio_el),
        # Optional
        comment=_tag_text(radio_el, "comment"),
        randomize=bool(_attr(radio_el, "randomize")),
        cols=parse_cols(radio_el),

    )

def parse_checkbox(checkbox_el) -> CheckboxQuestion:
    return CheckboxQuestion(
        label=_attr(checkbox_el, "label"),
        title=_tag_text(checkbox_el, "title"),
        atleast=int(_attr(checkbox_el, "atleast"))
    )


# Lookup parsing function given XML tag
_PARSERS = {
    "radio": parse_radio,
    "checkbox": parse_checkbox,
    "select": None,
    "row": parse_row,
    "col": parse_col,
    "choice": parse_choice,
}

def element_from_xml_element(xml_elm: ET.Element):
    """
    Converts a given XML element into the corresponding object
    Args:
        xml_elm: The XML element to convert

    Returns:
        the corresponding object
    """
    tag = xml_elm.tag
    if tag not in _PARSERS:
        raise ValueError(f"{tag} is not a valid tag")
    else:
        return _PARSERS[tag](xml_elm)


first_row_xml = root.find("row")
first_row = element_from_xml_element(first_row_xml)
radio_qn_xml = root
radio_qn = element_from_xml_element(radio_qn_xml)
print(radio_qn.rows)
