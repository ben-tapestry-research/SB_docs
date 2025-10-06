"""
Parses survey XML into Python objects

Each function takes an ElementTree Element representing the XML tag, and returns the corresponding object.
(e.g. parse_radio takes an <radio> tag and returns a RadioQuestion object)

Author: Ben Andrews
Date: September 2025
"""

import xml.etree.ElementTree as ET
from typing import List
import inspect
from enum import Enum

from survey_elements.models.questions import (
    Row,
    Col,
    Choice,
    RadioQuestion,
    AutoFill,
    CheckboxQuestion,
    NumberQuestion,
    FloatQuestion,
    TextQuestion,
    TextAreaQuestion,
    SelectQuestion,
    NoAnswer,
)

from survey_elements.models.structural import (
    Note,
    Suspend,
    Exec,
    Block,
    Res,
    Style,
    HTML,
    Validate,
)
from survey_elements.models.logic import (
    Loopvar,
    Looprow,
    Loop,
    Quota,
    GoTo,
    Define,
    Terminate,
    Logic,
    SampleSources,
    SampleSource,
    Var,
    Exit,
    Condition,
)

from survey_elements.models.enums import (
    Align,
    ViewMode,
    Shuffle,
    RowColChoiceShuffle,
    Where,
)
from survey_elements.utils.xml_helpers import (
    _attr,
    _tag_text,
    _parse_enum_set,
    _bit,
)


def _allowed_param_names(cls: type) -> set[str]:
    """Return the set of parameter names accepted by the __init__ of the given class.
    If the signature cannot be inspected, returns an empty set.

    Args:
        cls (type): A class type (e.g. RadioQuestion)"""
    try:
        params = set(inspect.signature(cls).parameters)
    except (TypeError, ValueError):
        params = set()
    params.discard("self")
    return params


# ########################### NEW STUFF #############################

def _split_csv_attr(val: str | None, enum_cls: type[Enum] | None = None) -> tuple[str, ...]:
    """Split CSV attribute into ordered tuple. If enum_cls is provided, map tokens to enum.value when possible.

    - preserves order
    - canonicalises tokens to enum.value when matched by name or value (case-insensitive)
    - keeps unknown tokens as-is (you can change to drop/raise)
    """
    if not val:
        return tuple()
    tokens = [p.strip() for p in val.split(",") if p.strip()]
    if enum_cls is None:
        return tuple(tokens)

    out: list[str] = []
    for t in tokens:
        tl = t.strip()
        matched = None
        for m in enum_cls:
            if tl.lower() == str(m.value).lower() or tl.lower() == m.name.lower():
                matched = str(m.value)
                break
        if matched:
            out.append(matched)
        else:
            # keep raw token if it doesn't match any enum member
            out.append(tl)
    return tuple(out)


# ------------ QUESTION TYPES ------------------
def question_base(el: ET.Element) -> dict:
    """Extracts fields from question elements (e.g. <radio>, <checkbox>, etc.). Used by all question parsers to avoid code duplication.
    Args:
        el (ET.Element): An ElementTree element representing a question tag
    Returns:
        dict: A dictionary of fields (some may be None)

    """
    # <exec> can be a child element of a question
    exec_el = el.find("exec")
    if exec_el is not None:
        exec_obj = Exec(content=exec_el.text, when=_attr(exec_el, "when"))
    else:
        exec_obj = None

    # <validate> can be a child element of a question
    validate_el = el.find("validate")
    if validate_el is not None:
        validate_obj = Validate(content=validate_el.text)
    else:
        validate_obj = None

    # <style> can be a child element of a question
    style_el = el.find("style")
    if style_el is not None:
        style_obj = parse_style(style_el)
    else:
        style_obj = None

    return {
        # Attributes (main)
        "label": _attr(el, "label"),
        "size": _attr(el, "size"),
        "verify": _attr(el, "verify"),
        "range": _attr(el, "range"),
        "translateable": _attr(el, "translateable"),
        "cond": _attr(el, "cond"),
        "randomize": _bit(el, "randomize"),
        "optional": _bit(el, "optional"),
        "where": _parse_enum_set(el, "where", Where),
        "atleast": _bit(el, "atleast"),
        "shuffle": _split_csv_attr(_attr(el, "shuffle"), Shuffle),
        "rowShuffle": _split_csv_attr(_attr(el, "rowShuffle"), RowColChoiceShuffle),
        "colShuffle": _split_csv_attr(_attr(el, "colShuffle"), RowColChoiceShuffle),
        "choiceShuffle": _split_csv_attr(_attr(el, "choiceShuffle"), RowColChoiceShuffle),
        "uses": _attr(el, "uses"),
        # atm1d / styling
        "ss_listDisplay": _attr(el, "ss:listDisplay"),
        "atm1d_numCols": _attr(el, "atm1d:numCols"),
        "atm1d_showInput": _attr(el, "atm1d:showInput"),
        "atm1d_viewMode": _split_csv_attr(_attr(el, "atm1d:viewMode"), ViewMode),
        "atm1d_large_minHeight": _attr(el, "atm1d:large_minHeight"),
        "atm1d_large_maxHeight": _attr(el, "atm1d:large_maxHeight"),
        "atm1d_large_minWidth": _attr(el, "atm1d:large_minWidth"),
        "atm1d_large_maxWidth": _attr(el, "atm1d:large_maxWidth"),
        "atm1d_large_buttonAlign": _split_csv_attr(_attr(el, "atm1d:large_buttonAlign"), Align),
        "atm1d_large_contentAlign": _split_csv_attr(_attr(el, "atm1d:large_contentAlign"), Align),
        "atm1d_small_minHeight": _attr(el, "atm1d:small_minHeight"),
        "atm1d_small_maxHeight": _attr(el, "atm1d:small_maxHeight"),
        "atm1d_small_minWidth": _attr(el, "atm1d:small_minWidth"),
        "atm1d_small_maxWidth": _attr(el, "atm1d:small_maxWidth"),
        "atm1d_small_buttonAlign": _split_csv_attr(_attr(el, "atm1d:small_buttonAlign"), Align),
        "atm1d_small_contentAlign": _split_csv_attr(_attr(el, "atm1d:small_contentAlign"), Align),
        # Tags
        "title": _tag_text(el, "title"),
        "comment": _tag_text(el, "comment"),
        "rows": parse_rows(el),
        "cols": parse_cols(el),
        "choices": parse_choices(el),
        # Child objects (that have attributes on the tags themselves)
        "exec": exec_obj,
        "validate": validate_obj,
        "style": style_obj,
        
    }


def element_base(el: ET.Element) -> dict:
    """
    Extracts fields for elements (e.g. <row>, <col>, <choice>, etc.). Used by all element parsers to avoid code duplication.

    Args:
        el (ET.Element): An ElementTree element representing a question tag"""
    return {
        # Mandatory
        "label": _attr(el, "label"),
        "content": el.text,
        # Optional
        "cond": _attr(el, "cond"),
        "randomize": _bit(el, "randomize"),
        "where": _parse_enum_set(el, "where", Where),
        "optional": _bit(el, "optional"),
        "alt": _attr(el, "alt"),
        "value": _attr(el, "value"),
        "verify": _attr(el, "verify"),
        "translateable": _attr(el, "translateable"),
        "shuffle": _parse_enum_set(el, "shuffle", Shuffle),
    }


def build_question(cls, el: ET.Element):
    """
    Builds a question object of the given class from the given XML element.

    Args:
        cls: The question class to instantiate (e.g. RadioQuestion)
        el (ET.Element): The ElementTree element representing the question
    Returns:
        An instance of the given question class
    """
    dct = question_base(el)

    # drop Nones
    dct = {k: v for k, v in dct.items() if v is not None}

    # keep only kwargs that cls accepts
    allowed = _allowed_param_names(cls)
    unknown = set(dct) - allowed
    if unknown:
        print(
            f"[build_question] {cls.__name__} ignoring unexpected fields: {sorted(unknown)}"
        )
    if allowed:
        dct = {k: v for k, v in dct.items() if k in allowed}

    # Dictionary now only contains keys that cls accepts

    # Return the constructed question object. Works by unpacking the dictionary into keyword arguments. E.g. RadioQuestion(**dct).
    return cls(**dct)


def build_element(cls, el: ET.Element):
    """Builds an element object of the given class from the given XML element.
    Args:
        cls: The element class to instantiate (e.g. Row, Col, Choice)
        el (ET.Element): The ElementTree element representing the element
    Returns:
        An instance of the given element class"""
    dct = element_base(el)
    # drop None values
    dct = {k: v for k, v in dct.items() if v is not None}

    # restrict to parameters the dataclass accepts
    allowed = _allowed_param_names(cls)
    unknown = [k for k in dct.keys() if k not in allowed]

    def _meaningful(v):
        return v is not None and v not in ("", (), [], {})

    unexpected_nonempty = [k for k in unknown if _meaningful(dct.get(k))]
    if unexpected_nonempty:
        print(
            f"[build_element] {cls.__name__} ignoring unexpected fields: {sorted(unexpected_nonempty)}"
        )

    # keep only allowed keys so cls(**dct) won't raise
    dct = {k: v for k, v in dct.items() if k in allowed}

    return cls(**dct)


def parse_radio(radio_el: ET.Element) -> RadioQuestion:
    """Parses a <radio> ElementTree element into a RadioQuestion object."""
    return build_question(RadioQuestion, radio_el)


def parse_checkbox(checkbox_el: ET.Element) -> CheckboxQuestion:
    """Parses a <checkbox> ElementTree element into a CheckboxQuestion object."""
    return build_question(CheckboxQuestion, checkbox_el)


def parse_select(select_el: ET.Element) -> SelectQuestion:
    """Parses a <select> ElementTree element into a SelectQuestion object."""
    return build_question(SelectQuestion, select_el)


def parse_autofill(autofill_el: ET.Element) -> AutoFill:
    """Parses an <autofill> ElementTree element into an AutoFill object."""
    return build_question(AutoFill, autofill_el)


def parse_number(number_el: ET.Element) -> NumberQuestion:
    """Parses a <number> ElementTree element into a NumberQuestion object."""
    return build_question(NumberQuestion, number_el)


def parse_float(float_el: ET.Element) -> FloatQuestion:
    """Parses a <float> ElementTree element into a FloatQuestion object."""
    return build_question(FloatQuestion, float_el)


def parse_text(text_el: ET.Element) -> TextQuestion:
    """Parses a <text> ElementTree element into a TextQuestion object."""
    return build_question(TextQuestion, text_el)


def parse_textarea(textarea_el: ET.Element) -> TextAreaQuestion:
    """Parses a <textarea> ElementTree element into a TextAreaQuestion object."""
    return build_question(TextAreaQuestion, textarea_el)


# -------------- ELEMENTS --------------------
def parse_row(row_el: ET.Element) -> Row:
    """Parses a <row> ElementTree element into a Row object."""
    return build_element(Row, row_el)


def parse_noanswer(na_el: ET.Element) -> NoAnswer:
    """Parses a <noanswer> ElementTree element into a NoAnswer object."""
    return build_element(NoAnswer, na_el)


def parse_rows(parent: ET.Element) -> tuple[Row | NoAnswer, ...]:
    """
    Collect both <row> and <noanswer> children and return tuple of Row/NoAnswer.
    Keeps original behaviour (order preserved).
    """
    rows = []
    for child in parent:
        if child.tag == "row":
            rows.append(parse_row(child))
        elif child.tag == "noanswer":
            rows.append(parse_noanswer(child))
        # keep existing handling of other tags (e.g. <insert>) elsewhere if present
    return tuple(rows)


def parse_col(col_el: ET.Element) -> Col:
    """Parses a <col> ElementTree element into a Col object."""
    return build_element(Col, col_el)


def parse_cols(parent: ET.Element) -> tuple[Col, ...]:
    """Parses all <col> children of the given parent element and returns a tuple of Col objects."""
    return tuple(parse_col(el) for el in parent.findall("col"))


def parse_choice(choice_el: ET.Element) -> Choice:
    """Parses a <choice> ElementTree element into a Choice object."""
    return build_element(Choice, choice_el)


def parse_choices(parent: ET.Element) -> tuple[Choice, ...]:
    """Parses all <choice> children of the given parent element and returns a tuple of Choice objects."""
    return tuple(parse_choice(r) for r in parent.findall("choice"))


def parse_block(block_el: ET.Element) -> Block:
    """
    Given an ElementTree <block> tag, convert into Block object. Recursively parses child elements.

    Args:
        block_el (ET.Element): A <block> tag as ElementTree
    Returns:
        Block: A Block object
    """
    children = []
    for child in block_el:
        if child.tag in _PARSERS:
            children.append(element_from_xml_element(child))
        else:
            # continue - ignore unknown tags
            raise ValueError(
                f"ERROR PARSING BLOCK {_attr(block_el, 'label')}. Found {child.tag} element in a block that does not have a parser"
            )
    return Block(
        label=_attr(block_el, "label"),
        cond=_attr(block_el, "cond"),
        children=tuple(children),
    )


def parse_note(note_el: ET.Element) -> Note:
    """
    Given an ElementTree <note> tag, convert into Note object. The content is the text within the tag.

    Args:
        note_el (ET.Element): A <note> tag as ElementTree

    Returns:
        Note: A Note object
    """
    content = note_el.text
    return Note(content=content)


def parse_suspend(susp_el: ET.Element) -> Suspend:
    """
    Given an ElementTree <suspend> tag, convert into Suspend object.

    Args:
        susp_el (ET.Element): A <suspend> tag as ElementTree

    Returns:
        Suspend: A Suspend object
    """
    return Suspend()


def parse_exec(exec_el: ET.Element) -> Exec:
    """
    Given an ElementTree <exec> tag, convert into Exec object. The content is the text within the tag.

    Args:
        exec_el (ET.Element): A <exec> tag as ElementTree
    Returns:
        Exec: A Exec object
    """
    content = exec_el.text
    when = _attr(exec_el, "when")
    cond = _attr(exec_el, "cond")
    return Exec(content=content, when=when, cond=cond)


def parse_html(html_el: ET.Element) -> HTML:
    """
    Given an ElementTree <html> tag, convert into HTML object. The content is the text within the tag.

    Args:
        html_el (ET.Element): A <html> tag as ElementTree
    Returns:
        HTML: A HTML object
    """
    content = html_el.text
    return HTML(label=_attr(html_el, "label"), content=content)


# ---------- LOGIC ELEMENTS --------------
def parse_define(define_el: ET.Element):
    """
    Given an ElementTree <define> tag, convert into Define object.
    Args:
        define_el (ET.Element): A <define> tag as ElementTree
    Returns:
        Define: A Define object
    """
    return Define(label=_attr(define_el, "label"), rows=parse_rows(define_el))


def parse_loop(loop_el: ET.Element) -> Loop:
    """
    Given an ElementTree <loop> tag, convert into Loop object. Recursively parses child elements.

    Args:
        loop_el (ET.Element): A <loop> tag as ElementTree
    Returns:
        Loop: A Loop object
    """

    children = []
    looprows: list[Looprow] = []
    # Parse child elements
    for child in loop_el:
        if child.tag in _PARSERS:
            children.append(element_from_xml_element(child))
        # if it's a looprow, parse and add to looprows
        elif child.tag == "looprow":
            looprows.append(parse_looprow(child))
        else:
            raise ValueError(
                f"ERROR PARSING LOOP {loop_el.tag}. Found {child.tag} element in a loop that does not have a parser"
            )
    return Loop(
        label=_attr(loop_el, "label"),
        children=tuple(children),
        looprows=tuple(looprows),
    )


def parse_loopvar(loopvar_el: ET.Element) -> Loopvar:
    """
    Given an ElementTree <loopvar> tag, convert into Loopvar object.

    Args:
        loopvar_el (ET.Element): A <loopvar> tag as ElementTree
    Returns:
        Loopvar: A Loopvar object
    """
    return Loopvar(name=_attr(loopvar_el, "name"), value=loopvar_el.text)


def parse_looprow(looprow_el: ET.Element) -> Looprow:
    """
    Given an ElementTree <looprow> tag, convert into Looprow object.
    Args:
        looprow_el (ET.Element): A <looprow> tag as ElementTree
    Returns:
        Looprow: A Looprow object
    """
    vars_x = tuple(parse_loopvar(v) for v in looprow_el.findall("loopvar"))
    return Looprow(label=_attr(looprow_el, "label"), vars=vars_x)


def parse_quota(quota_el: ET.Element) -> Quota:
    """
    Given an ElementTree <quota> tag, convert into Quota object.
    Args:
        quota_el (ET.Element): A <quota> tag as ElementTree
    Returns:
        Quota: A Quota object
    """
    return Quota(
        label=_attr(quota_el, "label"),
        overquota=_attr(quota_el, "overquota"),
        sheet=_attr(quota_el, "sheet"),
        content=quota_el.text,
    )


def parse_goto(goto_el: ET.Element) -> GoTo:
    """
    Given an ElementTree <goto> tag, convert into GoTo object.

    Args:
        goto_el (ET.Element): A <goto> tag as ElementTree
    Returns:
        GoTo: A GoTo object"""
    return GoTo(cond=_attr(goto_el, "cond"), target=_attr(goto_el, "target"))


def parse_term(term_el: ET.Element) -> Terminate:
    return Terminate(
        label=_attr(term_el, "label"), cond=_attr(term_el, "cond"), content=term_el.text
    )


def parse_res(res_el: ET.Element) -> Res:
    """
    Given an ElementTree <res> tag, convert into Res object. The content is the text within the tag.

    Args:
        res_el (ET.Element): A <res> tag as ElementTree
    Returns:
        Res: A Res object
    """
    return Res(label=_attr(res_el, "label"), content=res_el.text)


def parse_logic(logic_el: ET.Element) -> Logic:
    """
    Given an ElementTree <logic> tag, convert into Logic object.

    Args:
        logic_el (ET.Element): A <logic> tag as ElementTree
    Returns:
        Logic: A Logic object
    """
    return Logic(label=_attr(logic_el, "label"), uses=_attr(logic_el, "uses"))


def parse_style(style_el: ET.Element) -> Style:
    """Build a Style object from a <style> element without passing unrelated attrs."""
    name = _attr(style_el, "name")
    typ = _attr(style_el, "type")
    content = style_el.text
    return Style(name=name, content=content, type=typ)


def parse_sample_sources(sources_el: ET.Element) -> SampleSources:
    """
    Given an ElementTree <samplesources> tag, convert into SampleSources object
    Args:
        sources_el (ET.Element): A <samplesources> tag as ElementTree
    Returns:
        SampleSources: A SampleSources object
    """
    return SampleSources(
        default=_attr(sources_el, "default"),
        samplesources=tuple(
            parse_sample_source(s) for s in sources_el.findall("samplesource")
        ),
    )


def parse_sample_source(source_el: ET.Element) -> SampleSource:
    """
    Given an ElementTree <samplesource> tag, convert into SampleSource object
    Args:
        source_el (ET.Element): A <samplesource> tag as ElementTree
        Returns:
        SampleSource: A SampleSource object
    """
    return SampleSource(
        list=_attr(source_el, "list"),
        title=_tag_text(source_el, "title"),
        invalid=_tag_text(source_el, "invalid"),
        completed=_tag_text(source_el, "completed"),
        vars=tuple(parse_var(v) for v in source_el.findall("var")),
        exits=tuple(parse_exit(e) for e in source_el.findall("exit")),
    )


def parse_var(var_el: ET.Element) -> Var:
    """
    Given an ElementTree <var> tag, convert into Var object

    Args:
        var_el (ET.Element): A <var> tag as ElementTree
    Returns:
        Var: A Var object"""
    return Var(
        name=_attr(var_el, "name"),
        unique=_attr(var_el, "unique"),
        values=_attr(var_el, "values"),
    )


def parse_exit(exit_el: ET.Element) -> Exit:
    """
    Given an ElementTree <exit> tag, convert into Exit object

    Args:
        exit_el (ET.Element): A <exit> tag as ElementTree
    Returns:
        Exit: An Exit object"""
    return Exit(
        cond=_attr(exit_el, "cond"), url=_attr(exit_el, "url"), content=exit_el.text
    )


def parse_condition(condition_el: ET.Element) -> Condition:
    """
    Given an ElementTree <condition> tag, convert into Condition object
    Args:
        condition_el (ET.Element): A <condition> tag as ElementTree
    Returns:
        Condition: A Condition object
    """
    return Condition(
        label=_attr(condition_el, "label"),
        cond=_attr(condition_el, "cond"),
        content=condition_el.text,
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
    "autofill": parse_autofill,
    # Structural
    "block": parse_block,
    "note": parse_note,
    "suspend": parse_suspend,
    "exec": parse_exec,
    "res": parse_res,
    "style": parse_style,
    "html": parse_html,
    # Logic
    "loop": parse_loop,
    "quota": parse_quota,
    "goto": parse_goto,
    "define": parse_define,
    "term": parse_term,
    "logic": parse_logic,
    "samplesources": parse_sample_sources,
    "samplesource": parse_sample_source,
    "var": parse_var,
    "exit": parse_exit,
    "condition": parse_condition,
    "noanswer": parse_noanswer,
}

# Stack to show current path while parsing (for debugging)
_PARSE_STACK: List[str] = []


def _current_path() -> str:
    """Returns a strng reprresenting the current path in the XML being parsed, based on the _PARSE_STACK
     e.g. Parsing -> block(SCREENER) > block(BLK_QC_WEEKEND) > checkbox(QC_WEEKEND)
    Returns:
        str: A current path as a string
    """
    return " > ".join(_PARSE_STACK) or "<root>"


def element_from_xml_element(xml_elm: ET.Element):
    """
    Converts a given XML element into the corresponding object
    """
    tag = xml_elm.tag
    label = _attr(xml_elm, "label", "")
    # Gets the line number in the XML file where this element is defined (if available)
    # line = getattr(xml_elm, "sourceline", None)
    entry = f'<{tag} label="{label}">'

    # push and print progress
    _PARSE_STACK.append(entry)
    print(f"Parsing -> {_current_path()}")

    # Call the appropriate parser function based on the tag
    try:
        if tag not in _PARSERS:
            raise ValueError(f"No parser for <{tag}> element")
        result = _PARSERS[tag](xml_elm)
        print(f"Parsed  <- {_current_path()}")
        return result
    except Exception as e:
        # print error with current path
        raise ValueError(f"ERROR while parsing {_current_path()}: {e}")
    finally:
        _PARSE_STACK.pop()
