"""
Parses survey XML into Python objects

Each function takes an ElementTree Element representing the XML tag, and returns the corresponding object.
(e.g. parse_radio takes an <radio> tag and returns a RadioQuestion object)

Functions:
- parse_row - Parses a <row> tag into a Row object
- parse_rows - Parses all <row> tags within a parent element into a tuple of Row objects
- parse_col - Parses a <col> tag into a Col object
- parse_cols - Parses all <col> tags within a parent element into a tuple of Col objects
- parse_choice - Parses a <choice> tag into a Choice object
- parse_choices - Parses all <choice> tags within a parent element into a tuple of Choice objects
- parse_radio - Parses a <radio> tag into a RadioQuestion object
- parse_checkbox - Parses a <checkbox> tag into a CheckboxQuestion object
- parse_select - Parses a <select> tag into a SelectQuestion object
- parse_number - Parses a <number> tag into a NumberQuestion object
- parse_float - Parses a <float> tag into a FloatQuestion object
- parse_text - Parses a <text> tag into a TextQuestion object
- parse_textarea - Parses a <textarea> tag into a TextAreaQuestion object
- parse_block - Parses a <block> tag into a Block object, recursively parsing child elements
- parse_note - Parses a <note> tag into a Note object
- parse_suspend - Parses a <suspend> tag into a Suspend object
- parse_exec - Parses an <exec> tag into an Exec object
- parse_html - Parses an <html> tag into an HTML object
- parse_define - Parses a <define> tag into a Define object
- parse_loop - Parses a <loop> tag into a Loop object, recursively parsing child elements
- parse_loopvar - Parses a <loopvar> tag into a Loopvar object
- parse_looprow - Parses a <looprow> tag into a Looprow object
- parse_quota - Parses a <quota> tag into a Quota object
- parse_goto - Parses a <goto> tag into a GoTo object
- parse_term - Parses a <term> tag into a Terminate object
- parse_survey - Parses an entire survey XML file into a tuple of Element objects
- parse_res - Parses a <res> tag into a Res object
- parse_logic - Parses a <logic> tag into a Logic object
- parse_style - Parses a <style> tag into a Style object
- parse_sample_sources - Parses a <samplesources> tag into a SampleSources object
- parse_sample_source - Parses a <samplesource> tag into a SampleSource object
- parse_var - Parses a <var> tag into a Var object
- parse_exit - Parses an <exit> tag into an Exit object
- parse_condition - Parses a <condition> tag into a Condition object

Author: Ben Andrews
Date: September 2025
"""

import xml.etree.ElementTree as ET
from typing import List


from survey_elements.models.questions import (Element, Cell, Question, 
                                              Row, Col, Choice, RadioQuestion, 
                                              AutoFill, CheckboxQuestion, NumberQuestion, 
                                              FloatQuestion, TextQuestion, TextAreaQuestion, SelectQuestion)

from survey_elements.models.structural import Note, Suspend, Exec, Block, Res, Style, HTML
from survey_elements.models.logic import (Loopvar, Looprow, Loop, 
                                          Quota, GoTo, Define, 
                                          Terminate, Logic, SampleSources, 
                                          SampleSource, Var, Exit, Condition)

from survey_elements.models.enums import Where, Grouping, Legend, RowColChoiceShuffle, Shuffle, Sort, Mode
from survey_elements.utils.xml_helpers import (
    _attr,
    _tag_text,
    _parse_enum_set,
    _bit,
    _int_attr,
)


# ------------ ROWS ---------------


def parse_row(row_el: ET.Element) -> Row:
    """
    Given an ElementTree <row> tag, covert into Row object

    Args:
        row_el (ET): A <row> tag as ElementTree

    Returns:
        Row: A Row object
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
    Given an ElementTree representing a question (e.g. <radio>, <checkbox>), find all A <row> tags and return these as a tuple of Row objects

    Args:
        parent (ET.Element): A ET of a question (e.g. <radio>, <checkbox>)

    Returns:
        tuple[Row, ...]: List of Row objects
    """

    rows: List[Row] = []
    for child in parent:
        # Direct row declaration in XML
        if child.tag == "row":
            rows.append(parse_row(child))
        # Reference to a <define> tag - insert its rows here
        elif child.tag == "insert":
            label = child.get("source")
            d = _DEFINES.get(label)
            if d:
                rows.extend(d.rows)
            else:
                raise (f"<insert label='{label}'> not found in defines")

    return tuple(rows)


# ------------ COLUMNS ---------------


def parse_col(col_el: ET.Element) -> Col:
    """
    Given an ElementTree <col> tag, covert into Col object

    Args:
        col_el (ET): A <col> tag as ElementTree

    Returns:
        Col: A Column object
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
    Given an ElementTree representing a question (e.g. <radio>, <checkbox>), find all A <col> tags and return these as a tuple (list) of Column objects

    Args:
        parent (ET.Element): A ET of a question (e.g. <radio>, <checkbox>)

    Returns:
        tuple[Col, ...]: List of Column objects
    """
    return tuple(parse_col(r) for r in parent.findall("col"))


# ------------ CHOICES ----------------
def parse_choice(choice_el: ET.Element) -> Choice:
    """
    Given an ElementTree <choice> tag, covert into Choice object

    Args:
        col_el (ET): A <col> tag as ElementTree

    Returns:
        Col: A Column object
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
    Given an ElementTree representing a question (e.g. <radio>, <checkbox>), find all A <choice> tags and return these as a tuple (list) of Choice objects

    Args:
        parent (ET.Element): A ET of a <select> question

    Returns:
        tuple[Choice, ...]: List of Column objects
    """
    return tuple(parse_choice(r) for r in parent.findall("choice"))


# ------------ QUESTION TYPES ------------------
def parse_radio(radio_el: ET.Element) -> RadioQuestion:
    """
    Given an ElementTree <radio> tag, convert into RadioQuestion object
    Args:
        radio_el (ET.Element): A <radio> tag as ElementTree
        Returns:
        RadioQuestion: A RadioQuestion object
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
        where=_parse_enum_set(radio_el, "where", Where),
    )


def parse_autofill(autofill_el: ET.Element) -> AutoFill:
    """
    Given an ElementTree <autofill> tag, convert into AutoFill object

    Args:
        autofill_el (ET.Element): A <autofill> tag as ElementTree
    Returns:
        AutoFill: A AutoFill object
    """
    return AutoFill(
        label=_attr(autofill_el, "label"),
        title=_tag_text(autofill_el, "title"),
        rows=parse_rows(autofill_el),
        where=_parse_enum_set(autofill_el, "where", Where),
    )


def parse_checkbox(checkbox_el: ET.Element) -> CheckboxQuestion:
    """
    Given an ElementTree <checkbox> tag, convert into CheckboxQuestion object
    Args:
        checkbox_el (ET.Element): A <checkbox> tag as ElementTree
    Returns:
        CheckboxQuestion: A CheckboxQuestion object
    """
    return CheckboxQuestion(
        # Mandatory
        label=_attr(checkbox_el, "label"),
        title=_tag_text(checkbox_el, "title"),
        atleast=_int_attr(checkbox_el, "atleast", 1),
        rows=parse_rows(checkbox_el),
        # Optional
        comment=_tag_text(checkbox_el, "comment"),
        cols=parse_cols(checkbox_el),
        randomize=_bit(checkbox_el, "randomize"),
        where=_parse_enum_set(checkbox_el, "where", Where),
    )


def parse_select(select_el: ET.Element) -> SelectQuestion:
    """
    Given an ElementTree <select> tag, convert into SelectQuestion object

    Args:
        select_el (ET.Element): A <select> tag as ElementTree
    Returns:
        SelectQuestion: A SelectQuestion object
    """
    return SelectQuestion(
        # Mandatory
        label=_attr(select_el, "label"),
        title=_tag_text(select_el, "title"),
        choices=parse_choices(select_el),
        # Optional
        comment=_tag_text(select_el, "comment"),
        randomize=_bit(select_el, "randomize"),
        where=_parse_enum_set(select_el, "where", Where),
    )


def parse_number(number_el: ET.Element) -> NumberQuestion:
    """
    Given an ElementTree <number> tag, convert into NumberQuestion object

    Args:
        number_el (ET.Element): A <number> tag as ElementTree
    Returns:
        NumberQuestion: A NumberQuestion object
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
        where=_parse_enum_set(number_el, "where", Where),
    )


def parse_float(float_el: ET.Element) -> FloatQuestion:
    """
    Given an ElementTree <float> tag, convert into FloatQuestion object

    Args:
        float_el (ET.Element): A <float> tag as ElementTree
    Returns:
        FloatQuestion: A FloatQuestion object
    """
    return FloatQuestion(
        # Mandatory
        label=_attr(float_el, "label"),
        title=_tag_text(float_el, "title"),
        size=_int_attr(float_el, "size", 40),
        # Optional
        comment=_tag_text(float_el, "comment"),
        rows=parse_rows(float_el),
        cols=parse_cols(float_el),
        where=_parse_enum_set(float_el, "where", Where),
    )


def parse_text(text_el: ET.Element) -> TextQuestion:
    """
    Given an ElementTree <text> tag, convert into TextQuestion object

    Args:
        text_el (ET.Element): A <text> tag as ElementTree
        Returns:
        TextQuestion: A TextQuestion object

    Returns:
        TextQuestion: A TextQuestion object
    """
    return TextQuestion(
        # Mandatory
        label=_attr(text_el, "label"),
        title=_tag_text(text_el, "title"),
        size=_int_attr(text_el, "size", 40),
        # Optional
        comment=_tag_text(text_el, "comment"),
        rows=parse_rows(text_el),
        cols=parse_cols(text_el),
        where=_parse_enum_set(text_el, "where", Where),
    )


def parse_textarea(textarea_el: ET.Element) -> TextAreaQuestion:
    """
    Given an ElementTree <textarea> tag, convert into TextAreaQuestion object

    Args:
        textarea_el (ET.Element): A <textarea> tag as ElementTree
        Returns:
        TextAreaQuestion: A TextAreaQuestion object
    """
    return TextAreaQuestion(
        # Mandatory
        label=_attr(textarea_el, "label"),
        title=_tag_text(textarea_el, "title"),
        # Optional
        size=_int_attr(textarea_el, "size", 40),
        comment=_tag_text(textarea_el, "comment"),
        rows=parse_rows(textarea_el),
        cols=parse_cols(textarea_el),
        where=_parse_enum_set(textarea_el, "where", Where),
    )


# ---------- STRUCTURAL -----------


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
    return Block(label=_attr(block_el, "label"), children=tuple(children))


def parse_note(note_el: ET.Element) -> Note:
    """
    Given an ElementTree <note> tag, convert into Note object. The content is the text within the tag.

    Args:
        note_el (ET.Element): A <note> tag as ElementTree

    Returns:
        Note: A Note object
    """
    content = note_el.text.strip()
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
    content = exec_el.text.strip()
    return Exec(content=content)


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
        label=_attr(term_el, "label"),
        cond=_attr(term_el, "cond"),
        content=term_el.text.strip(),
    )


def parse_survey(root: ET.Element) -> tuple[Element, ...]:
    """
    Parse an entire survey XML file into a tuple of Element objects ### (this is for testing at the moment - not used) ####
    
    Args:
        root (ET): XML ET root
    Returns:
        tuple[Element, ...]: Tuple of Element objects
    """
    # Load and parse the XML file
    # root = ET.parse(src).getroot()
    # Find all <define> elements and register them
    find_defines(root)
    elements = []
    for child in root:
        tag = child.tag
        if tag in _PARSERS:
            elements.append(element_from_xml_element(child))
        else:
            # continue - uncomment to ignore unknown tags (for tessting)
            raise ValueError(f"'{tag}' tag found in <survey> - unsupported")
    return tuple(elements)


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
    """ 
    Given an ElementTree <style> tag, convert into Style object. The content is the text within the tag.
    Args:
        style_el (ET.Element): A <style> tag as ElementTree
    Returns:
        Style: A Style object
    """
    return Style(
        name=_attr(style_el, "name"),
        label=_attr(style_el, "label"),
        copy=_attr(style_el, "copy"),
        cond=_attr(style_el, "cond"),
        rows=_attr(style_el, "rows"),
        cols=_attr(style_el, "cols"),
        mode=_parse_enum_set(style_el, "mode", Mode),
        after=_attr(style_el, "after"),
        before=_attr(style_el, "before"),
        withx=_attr(style_el, "with"),
        wrap=_attr(style_el, "wrap"),
        content=style_el.text.strip(),
    )


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
}

# Global dictionary of <define> elements by their label (populated by find_defines)
_DEFINES: dict[str, Define] = {}

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


def find_defines(root_el: ET.Element) -> dict[str, Define]:
    """
    Search for all <define> elements in the XML and register them by their label (for lookup later)

    Args:
        root_el (ET.Element): The root ElementTree element (e.g. <survey>)
    Returns:
        dict[str, Define]: A dictionary of Define objects by their label
    """

    defs: dict[str, Define] = {}
    for el in root_el.iter():
        if el.tag == "define":
            label = el.get("label")
            print(label)
            # parse its rows
            rows = tuple(parse_row(child) for child in el)
            # create Define object and add to dictionary
            defs[label] = Define(label=label, rows=rows)

    # cache and return a copy
    _DEFINES.clear()
    _DEFINES.update(defs)
    return dict(defs)
