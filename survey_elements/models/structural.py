"""
A module for structural elements in a survey, such as blocks, notes, and page breaks.
Each provides a dataclass representation and a method to convert to an XML element.

Elements:
- Note: Represents a <note> tag with text notes
- Suspend: Represents a <suspend> tag for page breaks in the survey
- Exec: Represents an <exec> tag to contain executable Python code within the survey
- Block: Represents a <block> tag that can contain various child elements (sections off bits of the survey)
- Res: Represents a <res> tag with label and content (resource tag)
- Style: Represents a <style> tag to use JS and CSS in the survey
- HTML: Represents an <html> tag, which is an info screen in the survey

Each class includes a to_xml_element() method to convert the instance to an XML element.

Author: Ben Andrews
Date: September 2025
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, TypeAlias, List, Iterator, Tuple

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
    A <note> tag, used to leave a programmer note in the XML (not shown to respondents)
    https://forstasurveys.zendesk.com/hc/en-us/articles/4409476959003-Note-Tag-Create-Code-Comments

    Methods:
    to_xml_element() -> ET.Element: Convert to an XML element
    """

    content: str

    def to_xml_element(self) -> ET.Element:
        """Convert to an XML element"""
        el = ET.Element("note")
        el.text = self.content
        return el


@dataclass(frozen=True)
class Suspend:
    """
    A <suspend> tag (page break)
    https://forstasurveys.zendesk.com/hc/en-us/articles/4409476982555-Suspend-Tag-Adding-a-Page-Break

    Methods:
        to_xml_element() -> ET.Element: Convert to an XML element
    """
    

    def to_xml_element(self) -> ET.Element:
        """Convert to an XML element"""
        return ET.Element("suspend")


@dataclass(frozen=True)
class Exec:
    """
    An <exec> tag
    https://forstasurveys.zendesk.com/hc/en-us/articles/4409476937883-Exec-Tag-Execute-Python-Code

    Methods:
        to_xml_element() -> ET.Element: Convert to an XML element
    """

    content: str
    when: str | None = None

    def to_xml_element(self) -> ET.Element:
        """Convert to an XML element"""
        el = ET.Element("exec")
        el.text = self.content
        return el


@dataclass
class Block:
    """
    A <block> tag
    https://forstasurveys.zendesk.com/hc/en-us/articles/4409469844891-Block-Tag-Create-Sections

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
        """Convert to an XML element"""
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
    """
    A <res> tag (used to create reusable text resources)
    https://forstasurveys.zendesk.com/hc/en-us/articles/4409469873563-Resource-Tag-Create-Translatable-Resources
    
    Methods:
        to_xml_element() -> ET.Element: Convert to an XML element
    """

    label: str
    content: str

    def to_xml_element(self) -> ET.Element:
        """Convert to an XML element"""
        attrs = {"label": self.label}
        el = ET.Element("res", attrs)
        el.text = self.content
        return el


@dataclass
class Style:
    """
    A <style> tag
    https://forstasurveys.zendesk.com/hc/en-us/articles/4409461374491-XML-Style-System
    
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
        """Convert to an XML element"""
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
            "content": self.content,
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
    """
    A <html> tag
    https://forstasurveys.zendesk.com/hc/en-us/articles/4409461342491-HTML-Tag-Create-a-Comment-Element

    Methods:
        to_xml_element() -> ET.Element: Convert to an XML element
    """

    label: str
    content: str

    def to_xml_element(self) -> ET.Element:
        """Convert to an XML element"""
        attrs = {"label": self.label}
        el = ET.Element("html", attrs)
        el.text = self.content
        return el
