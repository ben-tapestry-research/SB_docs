from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, TypeAlias

from survey_elements.models.enums import Mode
from dataclasses import field

import xml.etree.ElementTree as ET
# Only import other package modules for type checking to avoid circular imports at runtime
if TYPE_CHECKING:
    from .logic import *
    from .questions import *


@dataclass(frozen=True)
class Note:
    """ 
    A <goto> tag

    Methods:
    to_xml_element() -> ET.Element: Convert to an XML element
    """
    content: str

    def to_xml_element(self) -> ET.Element:
        """ Convert to an XML element """
        el = ET.Element("note")
        el.text = self.content
        return el


@dataclass(frozen=True)
class Suspend:
    """ A <suspend> tag (page break)
     Methods:
         to_xml_element() -> ET.Element: Convert to an XML element
     """

    def to_xml_element(self) -> ET.Element:
        """ Convert to an XML element """
        return ET.Element("suspend")


@dataclass(frozen=True)
class Exec:
    """ 
    An <exec> tag

    Methods:
    to_xml_element() -> ET.Element: Convert to an XML element
    """
    content: str

    def to_xml_element(self) -> ET.Element:
        """ Convert to an XML element """
        el = ET.Element("exec")
        el.text = self.content
        return el


@dataclass(frozen=True)
class Block:
    """ 
    A <block> tag

    Methods:
    to_xml_element() -> ET.Element: Convert to an XML element
    """
    label: str | None = None
    # Define the alias as a STRING so it’s not evaluated at runtime
    BlockChild: TypeAlias = (
        "RadioQuestion | CheckboxQuestion | NumberQuestion | FloatQuestion | "
        "TextQuestion | TextAreaQuestion | SelectQuestion | Suspend | Exec | Note | "
        "Loop | Quota | GoTo | Define | Terminate | Block"
    )
    children: tuple[BlockChild, ...] = ()

    def to_xml_element(self) -> ET.Element:
        """ Convert to an XML element """
        attrs = {}
        attrs["label"] = self.label
        el = ET.Element("block", attrs)

        for child in self.children:
            # Raise error if child of block has no to_xml_element method
            try:
                el.append(child.to_xml_element())
            except Exception as e:
                raise TypeError(f"No to_xml_element for {type(child)}")
        return el


@dataclass(frozen=True)
class Res:
    """ A <res> tag
     Methods:
         to_xml_element() -> ET.Element: Convert to an XML element
     """
    label: str
    content: str

    def to_xml_element(self) -> ET.Element:
        """ Convert to an XML element """
        attrs = {
            "label": self.label
        }
        el = ET.Element("res", attrs)
        el.text = self.content
        return el


@dataclass
class Style:
    """ A <style> tag
    Methods:
        to_xml_element() -> ET.Element: Convert to an XML element
    """
    name: str
    label: str | None = None
    copy: str | None = None
    cond: str | None = None
    rows: str | None = None
    cols: str | None = None
    mode: set[Mode] = field(default_factory=set)
    after: str | None = None
    before: str | None = None
    withx: str | None = None
    wrap: str | None = None
    content: str | None = None

    def to_xml_element(self) -> ET.Element:
        """ Convert to an XML element """
        attrs = {}

        all_attrs = {
            "name": self.name,
            "label": self.label,
            "copy": self.copy,
            "cond": self.cond,
            "rows": self.rows,
            "cols": self.cols,
            # "mode": self.mode, # need to sort this one
            "after": self.after,
            "before": self.before,
            "with": self.withx,
            "wrap": self.wrap,
            "content": self.content
        }

        # Loop through adding attributes to final dict (if present)
        for k, v in all_attrs.items():
            if v not in [None, ""]:
                attrs[k] = v

        el = ET.Element("style", attrs)
        el.text = self.content
        return el


@dataclass
class HTML:
    """ A <html> tag
    Methods:
        to_xml_element() -> ET.Element: Convert to an XML element
    """
    label: str
    content: str

    def to_xml_element(self) -> ET.Element:
        """ Convert to an XML element """
        attrs = {
            "label": self.label
        }
        el = ET.Element("html", attrs)
        el.text = self.content
        return el