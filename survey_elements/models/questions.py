from dataclasses import dataclass, field
import xml.etree.ElementTree as ET
from typing import Callable, Dict, List, Optional, Sequence, Union, Tuple, Optional
import re

from survey_elements.models.enums import (
    Where,
    Grouping,
    Legend,
    RowColChoiceShuffle,
    Shuffle,
    Sort,
)
from survey_elements.utils.xml_helpers import _append_children
from survey_elements.utils.xml_helpers import bool_bit, str_, csv
from survey_elements.models.logic import DefineRef
from survey_elemets.utils.editables import EditableTemplate

"""
Defines the core data structures for survey questions and elements. 
Each class mirrors a Decipher survey element, with attributes corresponding to XML attributes.
Each class includes a `to_xml_element` method to convert the dataclass instance to an XML element.

Definitions: https://forstasurveys.zendesk.com/hc/en-us/articles/4409469868315-Overview-of-Question-and-Element-Tags

Classes:
- Element: Base class for all survey elements.
- Cell: Represents <row>, <col>, and <choice> elements.
- Question: Base class for all question types.
- Row: Represents a <row> element.
- Col: Represents a <col> element.
- Choice: Represents a <choice> element.
- RadioQuestion: Represents a <radio> question (single-select).
- CheckboxQuestion: Represents a <checkbox> question (multi-select).
- NumberQuestion: Represents a <number> question (numeric input).
- FloatQuestion: Represents a <float> question (decimal input).
- TextQuestion: Represents a <text> question (single-line text input).
- TextAreaQuestion: Represents a <textarea> question (multi-line text input).
- SelectQuestion: Represents a <select> question (dropdown selection).

Author: Ben Andrews
Date: August 2025
"""


@dataclass
class Element:
    """
    Base class - all questions and elements contain these


    Methods:
    - to_xml_element: Converts the object to an XML element
    """

    # Optional `TEXT_FIELD` (sets `el.text` for simple text nodes)
    # No inner text on Element
    TEXT_FIELD = None

    # Mandatory
    label: str
    disabled: bool | None = None
    randomize: bool | None = None
    style: str | None = None
    where: set[Where] = field(default_factory=set)
    alt: str | None = None
    altlabel: str | None = None
    translateable: str | None = None
    id: str | None = None
    sst: bool | None = None
    cond: str | None = None

    # For each field above, how to turn it into an XML attribute string
    # If the value is None, it will not be included in the XML element.
    ATTR_MAP = {
        "label": str_,
        "disabled": bool_bit,
        "randomize": bool_bit,
        "style": str_,
        "where": csv,
        "alt": str_,
        "altlabel": str_,
        "translateable": str_,
        "id": str_,
        "sst": bool_bit,
        "cond": str_,
    }

    def to_xml_element(self) -> ET.Element:
        """
        Converts a given object to an XML element (ElementTree).
        Uses the class's ATTR_MAP to determine how to convert attributes to XML attributes.
        If the class has a TEXT_FIELD defined, that attribute will be used as the inner text of the XML element.
        If the class has a CHILD_TEXT_MAP defined, those attributes will be added as child elements with text.
        Returns:
            ET.Element: The XML element representation of the object.
        """
        cls = type(self)
        # Determine the XML tag name and attribute mapping
        tag = getattr(cls, "XML_TAG", cls.__name__.lower())
        amap = getattr(cls, "ATTR_MAP", {})

        attrs = {}

        # Convert attributes to XML attributes using the ATTR_MAP mapping
        for py_name, spec in amap.items():
            xml_name, conv = spec if isinstance(spec, tuple) else (py_name, spec)
            raw = getattr(self, py_name, None)
            out = conv(raw)
            if out not in (None, ""):
                attrs[xml_name] = out

        # Create the XML element
        el = ET.Element(tag, attrs)

        # If this class declares a TEXT_FIELD, grab that attribute from the object and use it as the XML element text.
        text_field = getattr(cls, "TEXT_FIELD", None)
        if text_field:
            txt = getattr(self, text_field, None)
            if txt is not None:
                el.text = str(txt)

        # If this class declares a CHILD_TEXT_MAP, add those attributes as child elements with text.
        child_text_map = getattr(cls, "CHILD_TEXT_MAP", {})
        # For each entry in CHILD_TEXT_MAP, create a child element with the specified tag and text.
        for py_name, spec in child_text_map.items():
            child_tag, conv = spec if isinstance(spec, tuple) else (py_name, spec)
            raw = getattr(self, py_name, None)
            txt = conv(raw)
            if txt not in (None, ""):
                ET.SubElement(el, child_tag).text = txt

        return el


@dataclass
class Cell(Element):
    """
    Attributes for <row>, <col> and <choice> elements.
    These elements can contain text content.

    Methods:
    - to_xml_element: Converts the object to an XML element
    """

    # This means inner text becomes the node text.
    TEXT_FIELD = "content"

    content: str | None = None
    open: bool | None = None
    openSize: int | None = None
    # comma-separated list of unknown strings
    groups: set[str] = field(default_factory=set)
    value: int | None = None
    exclusive: bool | None = None
    aggregate: bool | None = None
    percentages: bool | None = None
    optional: bool | None = None
    range: str | None = None
    okUnique: bool | None = None
    openOptional: bool | None = None
    colLegend: bool | None = None
    extraError: bool | None = None
    amount: int | None = None
    size: int | None = None
    averages: bool | None = None

    # For each field above, how to turn it into an XML attribute string
    # If the value is None, it will not be included in the XML element.
    ATTR_MAP = {
        **Element.ATTR_MAP,
        "open": bool_bit,
        "openSize": str_,
        "groups": csv,
        "value": str_,
        "exclusive": bool_bit,
        "aggregate": bool_bit,
        "percentages": bool_bit,
        "optional": bool_bit,
        "range": str_,
        "okUnique": bool_bit,
        "openOptional": bool_bit,
        "colLegend": bool_bit,
        "extraError": bool_bit,
        "amount": str_,
        "size": str_,
        "averages": bool_bit,
    }


@dataclass(kw_only=True, eq=False)
class Question(Element):
    """
    The question attributes apply to <radio>, <select>, <checkbox>, <number>, <float>, <text> and <textarea> elements.


    Methods:
    - to_xml_element: Converts the object to an XML element
    """
    __hash__ = object.__hash__ # create unique hash to identify each question instance

    def __post_init__(self) -> None:
        """ Functions called post initiation """
        self._bind_define_refs() # Assign DefineRefs with self reference to DefineRef parent attribute
        self._set_editable_template()

    # Mandatory elements
    title: str

    editable: bool = False # Whether the use is allowed to edit the question text
    
    editable_obj: Optional[EditableTemplate] = None
    historic_title: Optional[str] = "" # Stores original title before render
    start_delimiter: str = r"{{"
    end_delimiter: str = r"}}"

    # Optional xml elements
    comment: str | None = None
    below: str | None = None
    choiceCond: str | None = None
    choiceShuffle: str | None = None
    colCond: str | None = None
    colLegend: str | None = None
    colShuffle: bool | None = None
    cond: str | None = None

    exec: str | None = None
    grouping: set[Grouping] = field(default_factory=set)
    optional: bool | None = None
    rightOf: str | None = None
    rowCond: str | None = None
    rowLegend: set[Legend] = field(default_factory=set)
    rowShuffle: set[RowColChoiceShuffle] = field(default_factory=set)
    shuffle: set[Shuffle] = field(default_factory=set)
    shuffleBy: str | None = None
    sortChoices: set[Sort] = field(default_factory=set)
    sortCols: set[Sort] = field(default_factory=set)
    sortRows: set[Sort] = field(default_factory=set)
    uses: str | None = None 
    values: str | None = None
    virtual: str | None = None

    # For each field above, how to turn it into an XML attribute string
    # If the value is None, it will not be included in the XML element.
    ATTR_MAP = {
        **Element.ATTR_MAP,
        "below": str_,
        "choiceCond": str_,
        "choiceShuffle": str_,
        "colCond": str_,
        "colLegend": str_,
        "colShuffle": bool_bit,
        "cond": str_,
        "exec": str_,
        "grouping": csv,
        "optional": bool_bit,
        "rightOf": str_,
        "rowCond": str_,
        "rowLegend": csv,
        "rowShuffle": csv,
        "shuffle": csv,
        "shuffleBy": str_,
        "sortChoices": csv,
        "sortCols": csv,
        "sortRows": csv,
        "uses": str_,
        "values": str_,
        "virtual": str_,
    }

    CHILD_TEXT_MAP = {
        "title": ("title", str_),  # <title>...</title>
        "comment": ("comment", str_),  # <comment></comment>
    }

    # Logs any previous DefineRefs if resolve has occured
    historic_define_refs: Optional[Tuple[DefineRef, ...]] = None

    @property
    def define_refs(self) -> Tuple[DefineRef, ...]:
        """ Tuple of DefineRef instances within a questions rows """
        return tuple(r for r in getattr(self, "rows", ()) if isinstance(r, DefineRef))
    
    def _bind_define_refs(self) -> None:
        """ Adds self to parent of instances of DefineRef """
        seq = getattr(self, "define_refs", None)
        if not seq:
            return
        for item in seq:
            print("adding parent")
            item.add_parent(q = self)

    def _set_editable_template(self) -> None:
        """ Creates a EditableText class for the question """
        self.editable_obj = (EditableTemplate(raw_template = self.title,
                                                 start = self.start_delimiter,
                                                 end = self.end_delimiter))

    def render_question(self):
        """ Renders editable question with user changes """
        if not self.editable:
            return
        if not self.historic_title:
            # Log historic title
            self.historic_title = self.title
        # Override title
        self.title = self.editable_obj.render()

    def to_xml_element(self) -> ET.Element:
        # 1) Build the base element + title/comment the way Element does
        el = super().to_xml_element()
        # 2) Append rows/cols/choices if they exist
        if hasattr(self, "rows"):
            _append_children(el, getattr(self, "rows"))
        if hasattr(self, "cols"):
            _append_children(el, getattr(self, "cols"))
        if hasattr(self, "choices"):
            _append_children(el, getattr(self, "choices"))

        return el


@dataclass()
class Row(Cell):
    """
    Attributes for <row> elements. Only need XML_TAG here.
    Inherits from Cell, which contains all the attributes and methods.
    """

    XML_TAG = "row"


@dataclass()
class Col(Cell):
    """
    Attributes for <col> elements. Only need XML_TAG here.
    Inherits from Cell, which contains all the attributes and methods.
    """

    XML_TAG = "col"


@dataclass()
class Choice(Cell):
    """
    Attributes for <col> elements. Only need XML_TAG here.
    Inherits from Cell, which contains all the attributes and methods.
    """

    XML_TAG = "choice"


# ------------- SPECIFIC QUESTION TYPES ------------- #


@dataclass(kw_only=True, eq=False)
class RadioQuestion(Question):
    """
    Attributes for <radio> questions (single-select). A <radio> question can contain <row> and <col> elements.
    https://forstasurveys.zendesk.com/hc/en-us/articles/4409476975899-Single-Select-Question-XML
    """

    XML_TAG = "radio"

    # Mandatory
    rows: tuple[Row, ...]

    # Optional
    cols: tuple[Col, ...] = ()


@dataclass(kw_only=True, eq=False)
class AutoFill(Question):
    """
    Attributes for <autofill> questions] (for piping).
    """

    XML_TAG = "autofill"

    rows: tuple[Row, ...] = ()


@dataclass(kw_only=True, eq=False)
class CheckboxQuestion(Question):
    """
    Attributes for <checkbox> questions (multi-select)
    https://forstasurveys.zendesk.com/hc/en-us/articles/4409476958107-Multi-Select-Question-XML
    """

    XML_TAG = "checkbox"
    atleast: int = 1
    # Mandatory
    rows: tuple[Row, ...]

    # Optional
    cols: tuple[Col, ...] = ()


@dataclass(kw_only=True, eq=False)
class NumberQuestion(Question):
    """
    Attributes for <number> questions (numeric input).
    https://forstasurveys.zendesk.com/hc/en-us/articles/4409469867291-Number-Element-XML
    """

    XML_TAG = "number"
    size: int | None = None

    # Optional
    rows: tuple[Row, ...] = ()
    cols: tuple[Col, ...] = ()


@dataclass(kw_only=True, eq=False)
class FloatQuestion(Question):
    """
    Attributes for <float> questions (decimal input).
    https://forstasurveys.zendesk.com/hc/en-us/articles/4409461339291-Float-Question-Attributes
    """

    XML_TAG = "float"
    size: int | None = None

    # Optional
    rows: tuple[Row, ...] = ()
    cols: tuple[Col, ...] = ()


@dataclass(kw_only=True, eq=False)
class TextQuestion(Question):
    """
    Attributes for <text> questions (single-line text input).
    https://forstasurveys.zendesk.com/hc/en-us/articles/4409476985755-Text-Question-XML
    """

    XML_TAG = "text"
    size: int | None = None

    # Optional
    rows: tuple[Row, ...] = ()
    cols: tuple[Col, ...] = ()


@dataclass(kw_only=True, eq=False)
class TextAreaQuestion(Question):
    """
    Attributes for <textarea> questions (multi-line text input).
    https://forstasurveys.zendesk.com/hc/en-us/articles/4409476986651-TextArea-Question-Attributes
    """

    XML_TAG = "textarea"
    size: int | None = None

    # Optional
    rows: tuple[Row, ...] = ()
    cols: tuple[Col, ...] = ()


@dataclass(kw_only=True, eq=False)
class SelectQuestion(Question):
    """
    Attributes for <select> questions (dropdown selection).
    https://forstasurveys.zendesk.com/hc/en-us/articles/4409461334299-Dropdown-Menu-Question-XML
    """

    XML_TAG = "select"
    choices: tuple[Choice, ...] = ()
