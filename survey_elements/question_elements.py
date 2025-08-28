from dataclasses import dataclass
import xml.etree.ElementTree as ET
from enum import Enum
from dataclasses import field


# TODO: information on what part of the question the user can modify
# Adding rows/cols/choices
# Adding exec
# TODO: functions that convert from XML

# DEFINITIONS FROM: https://forstasurveys.zendesk.com/hc/en-us/articles/4409469868315-Overview-of-Question-and-Element-Tags


class Where(str, Enum):
    EXECUTE = "execute"
    NOTDP = "notdp"
    NONE = "none"
    SUMMARY = "summary"
    SURVEY = "survey"
    REPORT = "report"
    DATA = "data"


class Grouping(str, Enum):
    AUTO = "auto"
    ROWS = "rows"
    COLS = "cols"


class Legend(str, Enum):
    DEFAULT = "default"
    BOTH = "both"
    LEFT = "left"
    RIGHT = "right"


class RowColChoiceShuffle(str, Enum):
    FLIP = "flip"
    RFLIP = "rflip"
    ROTATE = "rotate"
    REVERSE_ROTATE = "reverse-rotate"
    RROTATE = "rrotate"


class Shuffle(str, Enum):
    NONE = "none"
    ROWS = "rows"
    COLS = "cols"
    CHOICES = "choices"


class Sort(str, Enum):
    NONE = "none"
    ASC = "asc"
    DESC = "DESC"
    SURVEY = "survey"
    REPORT = "report"


def bool_bit(b: bool | None) -> str | None:
    """Get a string representation of a boolean value for XML attributes.

    Converts `True` to "1", `False` to "0", and `None` to `None`.

    Args:
        b (bool | None): The boolean value to convert.

    Returns:
        str | None: Returns "1" for `True`, "0" for `False`, and `None` for `None`.
    """
    return None if b is None else ("1" if b else "0")


def str_(s: object | None) -> str | None:
    """
Convert an object to a string for XML attributes.

    Args:
        s (object | None): The object to convert to a string.

    Returns:
        str | None: Returns `None` if the input is `None`, otherwise returns the string representation of the object.
    """
    return None if s is None else str(s)


def num(n: int | float | None) -> str | None:
    """Convert a number to a string for XML attributes.

    Args:
        n (int | float | None): The number to convert.
    Returns:
        str | None: Returns `None` if the input is `None`, otherwise returns the string representation of the number.
    """
    return None if n is None else str(n)


def csv(xs) -> str | None:
    """Convert a collection of values to a comma-separated string for XML attributes.

    Args:
        xs (iterable): An iterable of values to convert.
    Returns:
        str | None: Returns a comma-separated string of sorted values, or `None` if the input is empty.
    """
    if not xs:
        return None
    # emit values; if enums, use .value
    vals = (getattr(x, "value", x) for x in xs)
    return ",".join(str(v) for v in sorted(vals))


def _append_children(parent: ET.Element, children) -> None:
    """ 
    Append child elements to a parent XML element.
        Args:
            parent (ET.Element): The parent XML element to which children will be appended.
            children (iterable): An iterable of child elements to append.
    """
    if not children:
        return
    for child in children:
        parent.append(child.to_xml_element())


@dataclass()
class Element:
    """
Base class - all questions and elements contain these

Attributes:
    - TEXT_FIELD: Always `None` for this class, but subclasses may define a text field.
    - label: Mandatory
    - disabled: Optional; if `True`, the element is disabled.
    - randomize: Optional; if `True`, the element is randomized.
    - style: Optional; a string representing the style of the element.
    - where: Optional; a set of allowable values (e.g. "execute,survey,report").
    - alt: Optional; alternative text for the element.
    - altlabel: Optional; alternative label for the element.
    - translateable: Optional; indicates if the element is translatable.
    - id: Optional; an identifier for the element.
    - sst: Optional; if `True`, indicates that the element is a single-select type.


    Methods:
    - to_xml_element: Converts the object to an XML element
    """
    # No inner text on Element
    TEXT_FIELD = None

    # Mandatory
    label: str
    disabled: bool | None = None
    randomize: bool | None = None
    style: str | None = None
    # allowable values (e.g. "execute,survey,report")
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
        "cond": str_
    }

    def to_xml_element(self) -> ET.Element:
        cls = type(self)
        tag = getattr(cls, "XML_TAG", cls.__name__.lower())
        amap = getattr(cls, "ATTR_MAP", {})

        attrs = {}

        for py_name, spec in amap.items():
            xml_name, conv = (spec if isinstance(
                spec, tuple) else (py_name, spec))
            raw = getattr(self, py_name, None)
            out = conv(raw)
            if out not in (None, ""):
                attrs[xml_name] = out

        el = ET.Element(tag, attrs)

        # If this class declares a TEXT_FIELD, grab that attribute from the object and use it as the XML element text.
        text_field = getattr(cls, "TEXT_FIELD", None)
        if text_field:
            txt = getattr(self, text_field, None)
            if txt is not None:
                el.text = str(txt)

        child_text_map = getattr(cls, "CHILD_TEXT_MAP", {})
        for py_name, spec in child_text_map.items():
            child_tag, conv = (spec if isinstance(
                spec, tuple) else (py_name, spec))
            raw = getattr(self, py_name, None)
            txt = conv(raw)
            if txt not in (None, ""):
                ET.SubElement(el, child_tag).text = txt

        return el


@dataclass()
class Cell(Element):
    """
    Attributes for <row>, <col> and <choice> elements:
    """
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
    TEXT_FIELD = "content"


@dataclass(kw_only=True)
class Question(Element):
    """
    The question attributes apply to <radio>, <select>, <checkbox>, <number>, <float>, <text> and <textarea> elements.
    """
    # Mandatory elements
    title: str

    # Optional elements
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
    uses: str | None = None  # TODO: define list of these?
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
        "comment": ("comment", str_)  # <comment></comment>
    }

    def to_xml_element(self) -> ET.Element:
        # 1) Build the base element + title/comment the way Element does
        el = super().to_xml_element()

        if hasattr(self, "rows"):
            _append_children(el, getattr(self, "rows"))
        if hasattr(self, "cols"):
            _append_children(el, getattr(self, "cols"))
        if hasattr(self, "choices"):
            _append_children(el, getattr(self, "choices"))

        return el


@dataclass()
class Row(Cell):
    XML_TAG = "row"


@dataclass()
class Col(Cell):
    XML_TAG = "col"


@dataclass()
class Choice(Cell):
    XML_TAG = "choice"


@dataclass()
class RadioQuestion(Question):
    XML_TAG = "radio"

    rows: tuple[Row, ...] = ()
    cols: tuple[Col, ...] = ()


@dataclass()
class CheckboxQuestion(Question):
    XML_TAG = "checkbox"
    atleast: int = 1
    # atleast: bool = True
    rows: tuple[Row, ...] = ()
    cols: tuple[Col, ...] = ()


@dataclass()
class NumberQuestion(Question):
    XML_TAG = "number"
    rows: tuple[Row, ...] = ()
    cols: tuple[Col, ...] = ()
    # size: int = 3


@dataclass()
class Float(Question):
    XML_TAG = "float"
    rows: tuple[Row, ...] = ()
    cols: tuple[Col, ...] = ()


@dataclass()
class TextQuestion(Question):
    XML_TAG = "text"
    rows: tuple[Row, ...] = ()
    cols: tuple[Col, ...] = ()


@dataclass()
class TextAreaQuestion(Question):
    XML_TAG = "textarea"
    rows: tuple[Row, ...] = ()
    cols: tuple[Col, ...] = ()


@dataclass()
class SelectQuestion(Question):
    choices: tuple[Choice, ...] = ()
    pass
