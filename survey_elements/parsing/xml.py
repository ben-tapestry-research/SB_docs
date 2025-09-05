import xml.etree.ElementTree as ET
from typing import List


from survey_elements.models.questions import *
from survey_elements.models.structural import *
from survey_elements.models.logic import *

from survey_elements.models.enums import *
from survey_elements.utils.xml_helpers import _attr, _bit, _tag_text

# TODO: ensure all attributes / bits are captured - build code to flag??


# ------------ HELPER FUNCTIONS -------------


def _parse_enum_set(el: ET.Element, attr_name: str, enum_class) -> set:
    """ 
    Parses a comma-separated list of enum values from an attribute into a set of enum members
    e.g. where="execute,survey"  -> {Where.EXECUTE, Where.SURVEY}
    Args:
        el (ET.Element): The ElementTree object to search
        attr_name (str): The name of the attribute to fetch
        enum_class: The Enum class to use for parsing (e.g. Where)
        Returns:
        set: A set of enum members
    """
    raw_text = _attr(el, attr_name, "")
    if not raw_text:
        return set()
    # Split up the comma-separated string into its parts
    parts = [p.strip() for p in raw_text.split(",") if p.strip()]
    vals = set()
    # where="execute,survey"  -> {Where("execute"), Where("survey")}
    for p in parts:
        try:
            vals.add(enum_class(p))
        except ValueError:
            raise ValueError(f"Invalid value for {attr_name}: '{p}'")
    return vals

# ------------ ROWS ---------------


def parse_row(row_el: ET.Element) -> Row:
    """
    Given an ElementTree <row> tag, covert into Row object

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
    """ 
    Given an ElementTree representing a question (e.g. <radio>, <checkbox>), find all the <row> tags and return these as a tuple (list) of Row objects

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
            label = child.get("label")
            if not label:
                continue
            d = _DEFINES.get(label)
            if d:
                rows.extend(d.rows)
            else:
                raise(f"<insert label='{label}'> not found in defines")

    return tuple(rows)


# ------------ COLUMNS ---------------

def parse_col(col_el: ET.Element) -> Col:
    """
    Given an ElementTree <col> tag, covert into Col object

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
    """ 
    Given an ElementTree representing a question (e.g. <radio>, <checkbox>), find all the <col> tags and return these as a tuple (list) of Column objects

    Args:
        parent (ET.Element): The ET of a question (e.g. <radio>, <checkbox>)

    Returns:
        tuple[Col, ...]: List of Column objects
    """
    return tuple(parse_col(r) for r in parent.findall("col"))


# ------------ CHOICES ----------------
def parse_choice(choice_el: ET.Element) -> Choice:
    """
    Given an ElementTree <choice> tag, covert into Choice object

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
    """ 
    Given an ElementTree representing a question (e.g. <radio>, <checkbox>), find all the <choice> tags and return these as a tuple (list) of Choice objects

    Args:
        parent (ET.Element): The ET of a <select> question

    Returns:
        tuple[Choice, ...]: List of Column objects
    """
    return tuple(parse_choice(r) for r in parent.findall("choice"))


# ------------ QUESTION TYPES ------------------
def parse_radio(radio_el: ET.Element) -> RadioQuestion:
    """ 
    Given an ElementTree <radio> tag, convert into RadioQuestion object
    Args:
        radio_el (ET.Element): The <radio> tag as ElementTree
        Returns:
        RadioQuestion: The RadioQuestion object
    """
    return RadioQuestion(
        # Mandatory
        label=_attr(radio_el, "label"),
        title=_tag_text(radio_el, "title"),
        rows=parse_rows(radio_el),
        # Optional
        comment=_tag_text(radio_el, "comment"),
        randomize=_bit(radio_el, "randomize"),
        cols=parse_cols(radio_el),
        where=_parse_enum_set(radio_el, "where", Where)

    )


def parse_checkbox(checkbox_el: ET.Element) -> CheckboxQuestion:
    """ 
    Given an ElementTree <checkbox> tag, convert into CheckboxQuestion object
    Args:
        checkbox_el (ET.Element): The <checkbox> tag as ElementTree
        Returns:
        CheckboxQuestion: The CheckboxQuestion object
    """
    return CheckboxQuestion(
        # Mandatory
        label=_attr(checkbox_el, "label"),
        title=_tag_text(checkbox_el, "title"),
        atleast=int(_attr(checkbox_el, "atleast")),
        rows=parse_rows(checkbox_el),
        # Optional
        comment=_tag_text(checkbox_el, "comment"),
        cols=parse_cols(checkbox_el),
        randomize=_bit(checkbox_el, "randomize"),
        where=_parse_enum_set(checkbox_el, "where", Where)
    )


def parse_select(select_el: ET.Element) -> SelectQuestion:
    """ 
    Given an ElementTree <select> tag, convert into SelectQuestion object
    Args:
        select_el (ET.Element): The <select> tag as ElementTree
        Returns:
        SelectQuestion: The SelectQuestion object
    """
    return SelectQuestion(
        # Mandatory
        label=_attr(select_el, "label"),
        title=_tag_text(select_el, "title"),
        choices=parse_choices(select_el),
        # Optional
        comment=_tag_text(select_el, "comment"),
        randomize=_bit(select_el, "randomize"),
        where=_parse_enum_set(select_el, "where", Where)
    )


def parse_number(number_el: ET.Element) -> NumberQuestion:
    """ 
    Given an ElementTree <number> tag, convert into NumberQuestion object
    Args:
        number_el (ET.Element): The <number> tag as ElementTree
        Returns:
        NumberQuestion: The NumberQuestion object
    """
    return NumberQuestion(
        # Mandatory
        label=_attr(number_el, "label"),
        title=_tag_text(number_el, "title"),
        size=int(_attr(number_el, "size")),
        # Optional
        comment=_tag_text(number_el, "comment"),
        rows=parse_rows(number_el),
        cols=parse_cols(number_el),
        where=_parse_enum_set(number_el, "where", Where)
    )


def parse_float(float_el: ET.Element) -> FloatQuestion:
    """ 
    Given an ElementTree <float> tag, convert into FloatQuestion object
    Args:
        float_el (ET.Element): The <float> tag as ElementTree
        Returns:
        FloatQuestion: The FloatQuestion object
    """
    return FloatQuestion(
        # Mandatory
        label=_attr(float_el, "label"),
        title=_tag_text(float_el, "title"),
        size=int(_attr(float_el, "size")),
        # Optional
        comment=_tag_text(float_el, "comment"),
        rows=parse_rows(float_el),
        cols=parse_cols(float_el),
        where=_parse_enum_set(float_el, "where", Where)
    )


def parse_text(text_el: ET.Element) -> TextQuestion:
    """ 
    Given an ElementTree <text> tag, convert into TextQuestion object
    Args:
        text_el (ET.Element): The <text> tag as ElementTree
        Returns:
        TextQuestion: A TextQuestion object
    """
    return TextQuestion(
        # Mandatory
        label=_attr(text_el, "label"),
        title=_tag_text(text_el, "title"),
        size=int(_attr(text_el, "size")),
        # Optional
        comment=_tag_text(text_el, "comment"),
        rows=parse_rows(text_el),
        cols=parse_cols(text_el),
        where=_parse_enum_set(text_el, "where", Where)
    )


def parse_textarea(textarea_el: ET.Element) -> TextAreaQuestion:
    return TextAreaQuestion(
        # Mandatory
        label=_attr(textarea_el, "label"),
        title=_tag_text(textarea_el, "title"),
        # Optional
        size=int(_attr(textarea_el, "size")),
        comment=_tag_text(textarea_el, "comment"),
        rows=parse_rows(textarea_el),
        cols=parse_cols(textarea_el),
        where=_parse_enum_set(textarea_el, "where", Where)
    )


# ---------- STRUCTURAL -----------

def parse_block(block_el: ET.Element) -> Block:
    """ 
    Given an ElementTree <block> tag, convert into Block object. Recursively parses child elements.
    Args:
        block_el (ET.Element): The <block> tag as ElementTree
        Returns:
        Block: The Block object
    """
    children = []
    for child in block_el:
        if child.tag in _PARSERS:
            children.append(element_from_xml_element(child))
        else:
            raise ValueError(
                f"ERROR PARSING BLOCK {block_el.tag}. Found {child.tag} element in a block that does not have a parser")
    return Block(
        label=_attr(block_el, "label"),
        children=tuple(children)
    )


def parse_note(note_el: ET.Element) -> Note:
    """ 
    Given an ElementTree <note> tag, convert into Note object. The content is the text within the tag.
    Args: 
    note_el (ET.Element): The <note> tag as ElementTree
    Returns:
    Note: The Note object
    """
    content = note_el.text.strip()
    return Note(content=content)


def parse_suspend() -> Suspend:
    """ 
    Given an ElementTree <suspend> tag, convert into Suspend object.
    Returns:
    Suspend: The Suspend object
    """
    return Suspend()


def parse_exec(exec_el: ET.Element) -> Exec:
    """ 
    Given an ElementTree <exec> tag, convert into Exec object. The content is the text within the tag.
    Args:
        exec_el (ET.Element): The <exec> tag as ElementTree
        Returns:
        Exec: The Exec object
    """
    content = exec_el.text.strip()
    return Exec(content=content)


# ---------- LOGIC ELEMENTS --------------
def parse_define(define_el: ET.Element):
    """ 
    Given an ElementTree <define> tag, convert into Define object.
    Args:
        define_el (ET.Element): The <define> tag as ElementTree
        Returns:
        Define: The Define object
    """
    return Define(
        label=_attr(define_el, "label"),
        rows=parse_rows(define_el)
    )


def parse_loop(loop_el: ET.Element) -> Loop:
    """ 
    Given an ElementTree <loop> tag, convert into Loop object. Recursively parses child elements.
    Args:
        loop_el (ET.Element): The <loop> tag as ElementTree
        Returns:
        Loop: The Loop object
    """
    children = []
    for child in loop_el:
        if child.tag in _PARSERS:
            children.append(element_from_xml_element(child))
        else:
            raise ValueError(
                f"ERROR PARSING LOOP {loop_el.tag}. Found {child.tag} element in a loop that does not have a parser")
    return Loop(
        label=_attr(loop_el, "label"),
        children=tuple(children)
    )


def parse_quota(quota_el: ET.Element) -> Quota:
    return Quota(
        label=_attr(quota_el, "label"),
        overquota=_attr(quota_el, "overquota"),
        sheet=_attr(quota_el, "sheet"),
        content=quota_el.text.strip()
    )


def parse_goto(goto_el: ET.Element) -> GoTo:
    return GoTo(
        label=_attr(goto_el, "label"),
        cond=_attr(goto_el, "cond"),
        target=_attr(goto_el, "target")
    )


def parse_term(term_el: ET.Element) -> Terminate:
    return Terminate(
        label=_attr(term_el, "label"),
        cond=_attr(term_el, "cond"),
        content=term_el.text.strip()
    )




# Given an XML tag, find the corresponding parser function
_PARSERS = {

    # Individual elements
    "row": parse_row,
    "col": parse_col,
    "choice": parse_choice,

    # Question types
    "radio": parse_radio,
    "checkbox": parse_checkbox,
    "select": parse_select,
    "number": parse_number,
    "float": parse_float,
    "text": parse_text,
    "textarea": parse_textarea,

    # Structural
    "block": parse_block,
    "note": parse_note,
    "suspend": parse_suspend,
    "exec": parse_exec,

    # Logic
    "loop": parse_loop,
    "quota": parse_quota,
    "goto": parse_goto,
    "define": parse_define,
    "term": parse_term

}

# Global dictionary of <define> elements by their label (populated by find_defines)
_DEFINES: dict[str, Define] = {}


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


def find_defines(root_el: ET.Element) -> dict[str, Define]:
    """Search for all <define> elements in the XML and register them by their label (for lookup later)

    Args:
        root_el (ET.Element): _description_
    """


    defs: dict[str, Define] = {}
    for el in root_el.iter():
        if el.tag == "define":
            label = el.get("label")
            print(label)
            rows = tuple(
                parse_row(child)
                for child in el
            )
            defs[label] = Define(label=label, rows=rows)

     # cache and return a copy
    _DEFINES.clear()
    _DEFINES.update(defs)
    return dict(defs)


    # global _DEFINES
    # _DEFINES = {_attr(d, "label"): d for d in root_el.findall(".//define")}
