import xml.etree.ElementTree as ET
from typing import List

from survey_elements.question_elements import *
from survey_elements.logic_elements import *
from survey_elements.structural_elements import *

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

# Get core info from XML
root = ET.fromstring(xml)

root = ET.fromstring(xml)  # root.tag == "radio"
root.attrib  # {"label": "Q1", "id": "q1"}
root.find("title").text  # "How satisfied are you?"
# [<Element 'row' at ...>, <Element 'row' at ...>]
root.findall("row")

# ------------ HELPER FUNCTIONS -------------


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
        str: The text within the tag, or None if the tag does not exist or has no text.
    """
    node = el.find(tag)
    return node.text if (node is not None and node.text is not None) else None


# ------------ ROWS ---------------
def parse_row(row_el: ET.Element) -> Row:
    """Given an ElementTree <row> tag, covert into Row object

    Args:
        row_el (ET): The <row> tag as ElementTree

    Returns:
        Row: The Row object
    """
    return Row(
        label=_attr(row_el, "label"),
        content=row_el.text,
        cond=_attr(row_el, "cond"),
        alt=_attr(row_el, "alt"),
        randomize=_bit(row_el, "randomize"),
        groups=set(_attr(row_el, "groups").split(",")),
    )


def parse_rows(parent: ET.Element) -> tuple[Row, ...]:
    """ Given an ElementTree representing a question (e.g. <radio>, <checkbox>), find all the <row> tags and return these as a tuple (list) of Row objects

    Args:
        parent (ET.Element): The ET of a question (e.g. <radio>, <checkbox>)

    Returns:
        tuple[Row, ...]: List of Row objects
    """

    rows: List[Row] = []
    for child in parent:
        if child.tag == "row":
            rows.append(parse_row(child))
        elif child.tag == "insert":
            src = _attr(child, "source")
            if src not in _DEFINES:
                raise ValueError(f"<define> '{src} not found in XML'")
            # Fetch rows from the corresponding <define> list
            define_el = _DEFINES[src]
            for row in define_el.findall(row):
                rows.append(parse_row(row))



    return tuple(rows)


# ------------ COLUMNS ---------------
def parse_col(col_el: ET.Element) -> Col:
    """Given an ElementTree <col> tag, covert into Col object

    Args:
        col_el (ET): The <col> tag as ElementTree

    Returns:
        Col: The Column object
    """
    return Col(
        label=_attr(col_el, "label"),
        content=col_el.text,
        cond=_attr(col_el, "cond"),
        alt=_attr(col_el, "alt"),
        randomize=_bit(col_el, "randomize"),
        groups=set(_attr(col_el, "groups").split(",")),
    )


def parse_cols(parent: ET.Element) -> tuple[Col, ...]:
    """ Given an ElementTree representing a question (e.g. <radio>, <checkbox>), find all the <col> tags and return these as a tuple (list) of Column objects

    Args:
        parent (ET.Element): The ET of a question (e.g. <radio>, <checkbox>)

    Returns:
        tuple[Col, ...]: List of Column objects
    """
    return tuple(parse_col(r) for r in parent.findall("col"))


# ------------ CHOICES ----------------
def parse_choice(choice_el: ET.Element) -> Choice:
    """Given an ElementTree <choice> tag, covert into Choice object

    Args:
        col_el (ET): The <col> tag as ElementTree

    Returns:
        Col: The Column object
    """
    return Choice(
        label=_attr(choice_el, "label"),
        content=choice_el.text,
        cond=_attr(choice_el, "cond"),
        alt=_attr(choice_el, "alt"),
        randomize=_bit(choice_el, "randomize"),
        groups=set(_attr(choice_el, "groups").split(",")),
    )


def parse_choices(parent: ET.Element) -> tuple[Choice, ...]:
    """ Given an ElementTree representing a question (e.g. <radio>, <checkbox>), find all the <choice> tags and return these as a tuple (list) of Choice objects

    Args:
        parent (ET.Element): The ET of a <select> question

    Returns:
        tuple[Choice, ...]: List of Column objects
    """
    return tuple(parse_choice(r) for r in parent.findall("choice"))


# ------------ QUESTION TYPES ------------------
def parse_radio(radio_el: ET.Element) -> RadioQuestion:
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


def parse_checkbox(checkbox_el: ET.Element) -> CheckboxQuestion:
    return CheckboxQuestion(
        # Mandatory
        label=_attr(checkbox_el, "label"),
        title=_tag_text(checkbox_el, "title"),
        atleast=int(_attr(checkbox_el, "atleast")),
        rows=parse_rows(checkbox_el),
        # Optional
        cols=parse_cols(checkbox_el),
        randomize=bool(_attr(checkbox_el, "randomize"))
    )


# TODO: other question types







# ---------- STRUCTURAL -----------
def parse_define(define_el: ET.Element):
    return Define(
        label=_attr(define_el, "label"),
        rows=parse_rows(define_el)
    )

# Lookup parsing function given XML tag
_PARSERS = {
    "radio": parse_radio,
    "checkbox": parse_checkbox,
    "select": parse_select,
    "number": parse_number,
    "float": parse_float,
    "text": parse_text,
    "textarea": parse_textarea,
    "row": parse_row,
    "col": parse_col,
    "choice": parse_choice,
    "define": parse_define
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


_DEFINES: dict[str, ET.Element] = {}


def find_defines(root_el: ET.Element):
    """Search for all <define> elements in the XML and register them by their label (for lookup later)

    Args:
        root_el (ET.Element): _description_
    """
    global _DEFINES
    _DEFINES = {_attr(d, "label"): d for d in root_el.findall(".//define")}


# Tester stuff
first_row_xml = root.find("row")
first_row = element_from_xml_element(first_row_xml)
radio_qn_xml = root
radio_qn = element_from_xml_element(radio_qn_xml)
print(radio_qn.rows)
