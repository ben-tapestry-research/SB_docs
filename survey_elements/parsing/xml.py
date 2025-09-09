import xml.etree.ElementTree as ET
from typing import List


from survey_elements.models.questions import *
from survey_elements.models.structural import *
from survey_elements.models.logic import *

from survey_elements.models.enums import *
from survey_elements.utils.xml_helpers import _attr, _tag_text, _parse_enum_set, _bit, _int_attr


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
            label = child.get("source")
            if not label:
                continue
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

def parse_autofill(autofill_el: ET.Element) -> AutoFill:
    """ 
    Given an ElementTree <autofill> tag, convert into RadioQuestion object
    Args:
        autofill_el (ET.Element): The <autofill> tag as ElementTree
        Returns:
        AutoFill: The AutoFill object
    """
    return AutoFill(
        label=_attr(autofill_el, "label"),
        title=_tag_text(autofill_el, "title"),
        rows=parse_rows(autofill_el),
        where=_parse_enum_set(autofill_el, "where", Where)
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
        atleast=_int_attr(checkbox_el, "atleast", 1),
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
        size=_int_attr(float_el, "size", 40),
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
        size=_int_attr(text_el, "size", 40),
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
        size=_int_attr(textarea_el, "size", 40),
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
            # continue
            raise ValueError(
                f"ERROR PARSING BLOCK {_attr(block_el, "label")}. Found {child.tag} element in a block that does not have a parser")
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


def parse_suspend(susp_el: ET.Element) -> Suspend:
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

def parse_html(html_el: ET.Element) -> HTML:
    """ 
    Given an ElementTree <html> tag, convert into HTML object. The content is the text within the tag.
    Args:
        html_el (ET.Element): The <html> tag as ElementTree
        Returns:
        HTML: The HTML object
    """
    content = html_el.text
    return HTML(
        label=_attr(html_el, "label"),
        content=content
        )

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
    looprows: list[Looprow] = []
    for child in loop_el:
        if child.tag in _PARSERS:
            children.append(element_from_xml_element(child))
        elif child.tag == "looprow":
            # Find all the loopvars within this looprow
            vars_x = tuple(Loopvar(
                name=_attr(v, "name"),
                value=v.text
            ) for v in child.findall("loopvar"))
            looprows.append(Looprow(
                label=_attr(child, "label"),
                vars=vars_x
            ))
        else:
            raise ValueError(
                f"ERROR PARSING LOOP {loop_el.tag}. Found {child.tag} element in a loop that does not have a parser")
    return Loop(
        label=_attr(loop_el, "label"),
        children=tuple(children),
        looprows=tuple(looprows)
    )


def parse_loopvar(loopvar_el: ET.Element) -> Loopvar:
    """ 
    Given an ElementTree <loopvar> tag, convert into Loopvar object."""
    return Loopvar(
        name=_attr(loopvar_el, "name"),
        value=loopvar_el.text
    )


def parse_looprow(looprow_el: ET.Element) -> Looprow:
    """ 
    Given an ElementTree <looprow> tag, convert into Looprow object.
    Args:
        looprow_el (ET.Element): The <looprow> tag as ElementTree
        Returns:
        Looprow: The Looprow object
    """
    vars_x = tuple(parse_loopvar(v) for v in looprow_el.findall("loopvar"))
    return Looprow(
        label=_attr(looprow_el, "label"),
        vars=vars_x
    )


def parse_quota(quota_el: ET.Element) -> Quota:
    return Quota(
        label=_attr(quota_el, "label"),
        overquota=_attr(quota_el, "overquota"),
        sheet=_attr(quota_el, "sheet"),
        content=quota_el.text
    )


def parse_goto(goto_el: ET.Element) -> GoTo:
    return GoTo(

        cond=_attr(goto_el, "cond"),
        target=_attr(goto_el, "target")
    )


def parse_term(term_el: ET.Element) -> Terminate:
    return Terminate(
        label=_attr(term_el, "label"),
        cond=_attr(term_el, "cond"),
        content=term_el.text.strip()
    )


def parse_survey(src: str):
    """ Parse an entire survey XML file into a tuple of Element objects
    Args:
    src (str): Path to the XML file
    Returns:
    tuple[Element, ...]: Tuple of Element objects"""
    root = ET.parse(src).getroot()
    find_defines(root)
    elements = []
    for child in root:
        tag = child.tag
        if tag in _PARSERS:
            elements.append(element_from_xml_element(child))
        else:
            # continue
            raise ValueError(f"'{tag}' tag found in <survey> - unsupported")
    return tuple(elements)


def parse_res(res_el: ET.Element):
    """ 
    Given an ElementTree <res> tag, convert into Res object. The content is the text within the tag.
    Args:
        res_el (ET.Element): The <res> tag as ElementTree
        Returns:
        Res: The Res object
    """
    return Res(
        label=_attr(res_el, "label"),
        content=res_el.text
    )


def parse_logic(logic_el: ET.Element) -> Logic:
    """ 
    Given an ElementTree <logic> tag, convert into Logic object."""
    return Logic(
        label=_attr(logic_el, "label"),
        uses=_attr(logic_el, "uses")
    )


def parse_style(style_el: ET.Element) -> Style:
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
        content=style_el.text.strip()
    )

def parse_sample_sources(sources_el: ET.Element) -> SampleSources:
    """ 
    Given an ElementTree <samplesources> tag, convert into SampleSources object"""
    return SampleSources(
        default=_attr(sources_el, "default"),
        samplesources=tuple(parse_sample_source(s) for s in sources_el.findall("samplesource"))
    )

def parse_sample_source(source_el: ET.Element) -> SampleSource:
    """ Given an ElementTree <samplesource> tag, convert into SampleSource object"""
    return SampleSource(
        list=_attr(source_el, "list"),
        title=_tag_text(source_el, "title"),
        invalid=_tag_text(source_el, "invalid"),
        completed=_tag_text(source_el, "completed"),
        vars=tuple(parse_var(v) for v in source_el.findall("var")),
        exits=tuple(parse_exit(e) for e in source_el.findall("exit"))
    )

def parse_var(var_el: ET.Element) -> Var:
    """ Given an ElementTree <var> tag, convert into Var object"""
    return Var(
        name=_attr(var_el, "name"),
        unique=_attr(var_el, "unique"),
        values=_attr(var_el, "name")
    )

def parse_exit(exit_el: ET.Element) -> Exit:
    """ Given an ElementTree <exit> tag, convert into Exit object"""
    return Exit(
        cond=_attr(exit_el, "cond"),
        url=_attr(exit_el, "url"),
        content=exit_el.text
    )

def parse_condition(condition_el: ET.Element) -> Condition:
    """ Given an ElementTree <condition> tag, convert into Condition object"""
    return Condition(
        label=_attr(condition_el, "label"),
        cond=_attr(condition_el, "cond"),
        content=condition_el.text
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
    "condition": parse_condition

}

# Global dictionary of <define> elements by their label (populated by find_defines)
_DEFINES: dict[str, Define] = {}

# Stack to show current path while parsing (for debugging)
_PARSE_STACK: List[str] = []


def _current_path() -> str:
    """ Returns a string representing the current path in the XML being parsed, based on the _PARSE_STACK
     e.g. Parsing -> block(SCREENER) > block(BLK_QC_WEEKEND) > checkbox(QC_WEEKEND)
    Returns:
        str: The current path as a string
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
    # The entry to push onto the parse stack for tracking. The entry
    entry = f'<{tag} label="{label}">'

    # push and print progress
    _PARSE_STACK.append(entry)
    print(f"Parsing -> {_current_path()}")

    try:
        if tag not in _PARSERS:
            raise ValueError(f"{tag} is not a valid tag")
        result = _PARSERS[tag](xml_elm)
        print(f"Parsed  <- {_current_path()}")
        return result
    except Exception as e:
        # print a helpful diagnostic and the Python traceback, then re-raise
        raise ValueError(f"ERROR while parsing {_current_path()}: {e}")
    finally:
        _PARSE_STACK.pop()


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
