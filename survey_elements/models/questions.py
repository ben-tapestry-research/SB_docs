"""
Defines the core data structures for survey questions and elements.
Each class mirrors a Decipher survey element, with attributes corresponding to XML attributes.
Each class includes a `to_xml_element` method to convert the dataclass instance to an XML element.

Definitions: https://forstasurveys.zendesk.com/hc/en-us/articles/4409469868315-Overview-of-Question-and-Element-Tags

Classes:
- Element: Base class for all survey elements.
- Cell: Represents <row>, <col>, and <choice> elements.
- QuestionCluster: Handles a group of questions.
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

from dataclasses import dataclass, field
import xml.etree.ElementTree as ET
from typing import (
    Optional,
    Union,
    Tuple,
    Optional,
    TYPE_CHECKING,
)
import re
from enum import Enum

from survey_elements.models.enums import (
    Where,
    Grouping,
    Legend,
    Sort,
)
from survey_elements.utils.xml_helpers import _append_children
from survey_elements.utils.xml_helpers import bool_bit, str_, csv
from survey_elements.models.logic import DefineRef
from survey_elements.models.structural import (
    Exec,
    Validate,
    Style,
    Suspend
)
from survey_elements.utils.editables import EditableTemplate
from survey_elements.models import enums as _enums  # adjust import path if needed

if TYPE_CHECKING:
    from .logic import *
    from .questions import *


def _join_csv_field(v) -> str | None:
    """Converter used by ATTR_MAP: accepts tuple/list/set/str -> returns CSV or None."""
    if v is None:
        return None
    if isinstance(v, str):
        return v if v != "" else None
    try:
        seq = tuple(v)
    except TypeError:
        return str(v)
    if not seq:
        return None
    return ",".join(str(x) for x in seq)


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
    where: set[Where] = field(default_factory=set)
    alt: str | None = None
    altlabel: str | None = None
    translateable: str | None = None
    id: str | None = None
    sst: bool | None = None
    cond: str | None = None
    verify: str | None = None

    # For each field above, how to turn it into an XML attribute string
    # If the value is None, it will not be included in the XML element.
    ATTR_MAP = {
        "label": str_,
        "disabled": bool_bit,
        "randomize": bool_bit,
        # only emit style attribute when the python field is a plain string
        "style": (
            "style",
            lambda v: None if v is None or not isinstance(v, str) else str(v),
        ),
        "where": csv,
        "alt": str_,
        "altlabel": str_,
        "translateable": str_,
        "id": str_,
        "sst": bool_bit,
        "cond": str_,
        "verify": str_,
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

    # TODO Add links to Suspend, Exec, Terminate, Note and Block objects that linked to this class
    __hash__ = object.__hash__  # create unique hash to identify each question instance

    def __post_init__(self) -> None:
        """Functions called post initiation"""
        self._bind_define_refs()  # Assign DefineRefs with self reference to DefineRef parent attribute
        self._set_editable_template()

    # Mandatory elements
    title: str

    # Title Editability
    editable: bool = False  # Whether the use is allowed to edit the question text
    editable_obj: Optional[EditableTemplate] = None
    historic_title: Optional[str] = ""  # Stores original title before render
    start_delimiter: str = r"{{"
    end_delimiter: str = r"}}"

    suspend: Suspend

    # Optional xml elements
    comment: str | None = None
    below: str | None = None
    choiceCond: str | None = None

    colCond: str | None = None
    colLegend: str | None = None
    cond: str | None = None
    exec: Exec | None = None
    validate: Validate | None = None
    style: Style | None = None
    grouping: set[Grouping] = field(default_factory=set)
    optional: bool | None = None
    rightOf: str | None = None
    rowCond: str | None = None
    rowLegend: set[Legend] = field(default_factory=set)
    shuffleBy: str | None = None
    sortChoices: set[Sort] = field(default_factory=set)
    sortCols: set[Sort] = field(default_factory=set)
    sortRows: set[Sort] = field(default_factory=set)
    uses: str | None = None
    values: str | None = None
    virtual: str | None = None
    size: str | None = None

    # Survey styling (ss attributes)
    ss_listDisplay: str | None = None

    # Button rating attributes (atm1d) - https://forstasurveys.zendesk.com/hc/en-us/articles/4409461312923-Customizing-the-Button-Select-Element
    atm1d_numCols: str | None = None
    atm1d_showInput: str | None = None
    atm1d_viewMode: tuple[str, ...] = field(default_factory=tuple)
    atm1d_large_minHeight: str | None = None
    atm1d_large_maxHeight: str | None = None
    atm1d_large_minWidth: str | None = None
    atm1d_large_maxWidth: str | None = None
    atm1d_large_buttonAlign: tuple[str, ...] = field(default_factory=tuple)
    atm1d_large_contentAlign: tuple[str, ...] = field(default_factory=tuple)
    atm1d_small_minHeight: str | None = None
    atm1d_small_maxHeight: str | None = None
    atm1d_small_minWidth: str | None = None
    atm1d_small_maxWidth: str | None = None
    atm1d_small_buttonAlign: tuple[str, ...] = field(default_factory=tuple)
    atm1d_small_contentAlign: tuple[str, ...] = field(default_factory=tuple)

    cardsort_displayNavigation: str | None = None
    cardsort_displayCounter: str | None = None
    cardsort_displayProgress: str | None = None
    cardsort_animationDuration: str | None = None
    cardsort_wrapBuckets: str | None = None
    cardsort_bucketsPerRow: str | None = None
    cardsort_themeFile: str | None = None
    cardsort_automaticAdvance: str | None = None
    cardsort_iconButtonCSS: str | None = None
    cardsort_iconButtonDisableCSS: str | None = None
    cardsort_iconButtonHoverCSS: str | None = None
    cardsort_buttonPreviousHTML: str | None = None
    cardsort_buttonNextHTML: str | None = None
    cardsort_cardCSS: str | None = None
    cardsort_cardDisableCSS: str | None = None
    cardsort_cardHoverCSS: str | None = None
    cardsort_cardSelectCSS: str | None = None
    cardsort_dragAndDrop: str | None = None
    cardsort_bucketCSS: str | None = None
    cardsort_bucketDisableCSS: str | None = None
    cardsort_bucketHoverCSS: str | None = None
    cardsort_bucketSelectCSS: str | None = None
    cardsort_bucketCountCSS: str | None = None
    cardsort_bucketCountDisableCSS: str | None = None
    cardsort_bucketCountHoverCSS: str | None = None
    cardsort_progressCSS: str | None = None
    cardsort_contentsCardCSS: str | None = None
    cardsort_completionHTML: str | None = None
    cardsort_completionCSS: str | None = None

    # shuffle fields as CSV strings
    shuffle: tuple[str, ...] = field(default_factory=tuple)
    rowShuffle: tuple[str, ...] = field(default_factory=tuple)
    colShuffle: tuple[str, ...] = field(default_factory=tuple)
    choiceShuffle: tuple[str, ...] = field(default_factory=tuple)

    # For each field above, how to turn it into an XML attribute string
    # If the value is None, it will not be included in the XML element.
    ATTR_MAP = {
        **Element.ATTR_MAP,
        "below": str_,
        "choiceCond": str_,
        "choiceShuffle": ("choiceShuffle", _join_csv_field),
        "colCond": str_,
        "colLegend": str_,
        "colShuffle": ("colShuffle", _join_csv_field),
        "shuffle": ("shuffle", _join_csv_field),
        "shuffleBy": str_,
        "sortChoices": csv,
        "sortCols": csv,
        "sortRows": csv,
        "uses": str_,
        "values": str_,
        "virtual": str_,
        "ss_listDisplay": ("ss:listDisplay", str_),
        "size": str_,
        "rowShuffle": ("rowShuffle", _join_csv_field),
        "colShuffle": ("colShuffle", _join_csv_field),
        # atm1d
        "atm1d_numCols": ("atm1d:numCols", str_),
        "atm1d_showInput": ("atm1d:showInput", str_),
        "atm1d_viewMode": ("atm1d:viewMode", _join_csv_field),
        "atm1d_large_minHeight": ("atm1d:large_minHeight", str_),
        "atm1d_large_maxHeight": ("atm1d:large_maxHeight", str_),
        "atm1d_large_minWidth": ("atm1d:large_minWidth", str_),
        "atm1d_large_maxWidth": ("atm1d:large_maxWidth", str_),
        "atm1d_large_buttonAlign": ("atm1d:large_buttonAlign", _join_csv_field),
        "atm1d_large_contentAlign": ("atm1d:large_contentAlign", _join_csv_field),
        "atm1d_small_minHeight": ("atm1d:small_minHeight", str_),
        "atm1d_small_maxHeight": ("atm1d:small_maxHeight", str_),
        "atm1d_small_minWidth": ("atm1d:small_minWidth", str_),
        "atm1d_small_maxWidth": ("atm1d:small_maxWidth", str_),
        "atm1d_small_buttonAlign": ("atm1d:small_buttonAlign", _join_csv_field),
        "atm1d_small_contentAlign": ("atm1d:small_contentAlign", _join_csv_field),
        # cardsort
        "cardsort_displayNavigation": ("cardsort:displayNavigation", str_),
        "cardsort_displayCounter": ("cardsort:displayCounter", str_),
        "cardsort_displayProgress": ("cardsort:displayProgress", str_),
        "cardsort_animationDuration": ("cardsort:animationDuration", str_),
        "cardsort_wrapBuckets": ("cardsort:wrapBuckets", str_),
        "cardsort_bucketsPerRow": ("cardsort:bucketsPerRow", str_),
        "cardsort_themeFile": ("cardsort:themeFile", str_),
        "cardsort_automaticAdvance": ("cardsort:automaticAdvance", str_),
        "cardsort_iconButtonCSS": ("cardsort:iconButtonCSS", str_),
        "cardsort_iconButtonDisableCSS": ("cardsort:iconButtonDisableCSS", str_),
        "cardsort_iconButtonHoverCSS": ("cardsort:iconButtonHoverCSS", str_),
        "cardsort_buttonPreviousHTML": ("cardsort:buttonPreviousHTML", str_),
        "cardsort_buttonNextHTML": ("cardsort:buttonNextHTML", str_),
        "cardsort_cardCSS": ("cardsort:cardCSS", str_),
        "cardsort_cardDisableCSS": ("cardsort:cardDisableCSS", str_),
        "cardsort_cardHoverCSS": ("cardsort:cardHoverCSS", str_),
        "cardsort_cardSelectCSS": ("cardsort:cardSelectCSS", str_),
        "cardsort_dragAndDrop": ("cardsort:dragAndDrop", str_),
        "cardsort_bucketCSS": ("cardsort:bucketCSS", str_),
        "cardsort_bucketDisableCSS": ("cardsort:bucketDisableCSS", str_),
        "cardsort_bucketHoverCSS": ("cardsort:bucketHoverCSS", str_),
        "cardsort_bucketSelectCSS": ("cardsort:bucketSelectCSS", str_),
        "cardsort_bucketCountCSS": ("cardsort:bucketCountCSS", str_),
        "cardsort_bucketCountDisableCSS": ("cardsort:bucketCountDisableCSS", str_),
        "cardsort_bucketCountHoverCSS": ("cardsort:bucketCountHoverCSS", str_),
        "cardsort_progressCSS": ("cardsort:progressCSS", str_),
        "cardsort_contentsCardCSS": ("cardsort:contentsCardCSS", str_),
        "cardsort_completionHTML": ("cardsort:completionHTML", str_),
        "cardsort_completionCSS": ("cardsort:completionCSS", str_),
    }

    CHILD_TEXT_MAP = {
        "title": ("title", str_),  # <title>...</title>
        "comment": ("comment", str_),  # <comment></comment>
    }

    # Logs any previous DefineRefs if resolve has occured
    historic_define_refs: Optional[Tuple[DefineRef, ...]] = None

    @property
    def define_refs(self) -> Tuple[DefineRef, ...]:
        """Tuple of DefineRef instances within a questions rows"""
        return tuple(r for r in getattr(self, "rows", ()) if isinstance(r, DefineRef))

    def _bind_define_refs(self) -> None:
        """Adds self to parent of instances of DefineRef"""
        seq = getattr(self, "define_refs", None)
        if not seq:
            return
        for item in seq:
            print("adding parent")
            item.add_parent(q=self)

    def _set_editable_template(self) -> None:
        """Creates a EditableText class for the question"""
        self.editable_obj = EditableTemplate(
            raw_template=self.title, start=self.start_delimiter, end=self.end_delimiter
        )

    def render_question(self):
        """Renders editable question with user changes"""
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

        # 1.5) append exec child if present (Exec dataclass has to_xml_element)
        exec_obj = getattr(self, "exec", None)
        if exec_obj is not None:
            el.append(exec_obj.to_xml_element())
        # 1.6) append validate child if present (Exec dataclass has to_xml_element)
        validate_obj = getattr(self, "validate", None)
        if validate_obj is not None:
            el.append(validate_obj.to_xml_element())

        style_obj = getattr(self, "style", None)
        if style_obj is not None:
            el.append(style_obj.to_xml_element())

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
class NoAnswer(Cell):
    """
    Attributes for <noanswer> elements. Only need XML_TAG here.
    Inherits from Cell, which contains all the attributes and methods.
    """

    XML_TAG = "noanswer"


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

    # rows may contain Row or NoAnswer
    rows: tuple[Union[Row, "NoAnswer"], ...]
    cols: tuple[Col, ...] = ()


@dataclass(kw_only=True, eq=False)
class AutoFill(Question):
    """
    Attributes for <autofill> questions] (for piping).
    """

    XML_TAG = "autofill"

    rows: tuple[Union[Row, "NoAnswer"], ...] = ()


@dataclass(kw_only=True, eq=False)
class CheckboxQuestion(Question):
    """
    Attributes for <checkbox> questions (multi-select)
    https://forstasurveys.zendesk.com/hc/en-us/articles/4409476958107-Multi-Select-Question-XML
    """

    XML_TAG = "checkbox"
    atleast: int = 1
    rows: tuple[Union[Row, "NoAnswer"], ...]
    cols: tuple[Col, ...] = ()


@dataclass(kw_only=True, eq=False)
class NumberQuestion(Question):
    """
    Attributes for <number> questions (numeric input).
    https://forstasurveys.zendesk.com/hc/en-us/articles/4409469867291-Number-Element-XML
    """

    XML_TAG = "number"
    size: int | None = None
    rows: tuple[Union[Row, "NoAnswer"], ...] = ()
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
    rows: tuple[Union[Row, "NoAnswer"], ...] = ()
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
    rows: tuple[Union[Row, "NoAnswer"], ...] = ()
    cols: tuple[Col, ...] = ()


@dataclass(kw_only=True, eq=False)
class SelectQuestion(Question):
    """
    Attributes for <select> questions (dropdown selection).
    https://forstasurveys.zendesk.com/hc/en-us/articles/4409461334299-Dropdown-Menu-Question-XML
    """

    XML_TAG = "select"
    choices: tuple[Choice, ...] = ()


def _csv_to_enum_set(csv_text: str | None, enum_cls) -> set:
    """Convert CSV/text -> set of enum members. Ignores empty values."""
    if not csv_text:
        return set()
    parts = [p.strip() for p in csv_text.split(",") if p.strip()]
    out = set()
    for p in parts:
        # try matching by name, value or label attribute
        for member in enum_cls:
            if (
                p == member.name
                or p == getattr(member, "value", None)
                or p == getattr(member, "label", None)
            ):
                out.add(member)
                break
        else:
            # fallback: leave as raw string (optional)
            pass
    return out


def _single_to_enum(value: str | None, enum_cls):
    s = (value or "").strip()
    if not s:
        return None
    for member in enum_cls:
        if (
            s == member.name
            or s == getattr(member, "value", None)
            or s == getattr(member, "label", None)
        ):
            return member
    return None
