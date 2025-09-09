from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, Tuple, TypeAlias
from xml.etree import ElementTree as ET

# Only import types at type-check time to avoid runtime circular imports
if TYPE_CHECKING:
    from .questions import *
    from .structural import *


@dataclass
class Loopvar:
    """ 
    A <loopvar> element (within a looprow) 

    Methods:
        to_xml_element() -> ET.Element: Convert to an XML element
    """
    name: str
    value: str | None = None

    def to_xml_element(self) -> ET.Element:
        attr = {
            "name": self.name
        }
        el = ET.Element("loopvar", attr)
        el.text = self.value
        return el


@dataclass
class Looprow:
    """ 
    A <looprow> element (within a loop)

    Methods:
        to_xml_element() -> ET.Element: Convert to an XML element
    """
    label: str
    cond: str | None = None
    vars: tuple[Loopvar, ...] = ()

    def to_xml_element(self) -> ET.Element:
        attrs = {
            "label": self.label
        }

        if self.cond not in [None, ""]:
            attrs["cond"] = self.cond

        el = ET.Element("looprow", attrs)

        for loopvar in self.vars:
            child = loopvar.to_xml_element()
            el.append(child)

        return el





@dataclass
class Loop:
    # A Loop can contain any question or structural element as a child.#
    label: str


    # Define the alias as a string - avoids weird runtime issues I was getting
    LoopChild: TypeAlias = (
    "RadioQuestion | CheckboxQuestion | NumberQuestion | FloatQuestion | "
    "TextQuestion | TextAreaQuestion | SelectQuestion | Suspend | Exec | Note | "
    "Loop | Quota | GoTo | Define | Terminate | Block"
    )
    children: tuple[LoopChild, ...] = ()
    looprows: tuple[Looprow, ...] = ()

    def to_xml_element(self) -> ET.Element:
        attrs = {
            "label": self.label
        }
        el = ET.Element("loop", attrs)

        for child in self.children:
            # Raise error if child of loop has no to_xml_element method
            try:
                el.append(child.to_xml_element())
            except Exception as e:
                raise TypeError(f"Child of Loop has no to_xml_element method: {child}") from e

        for row in self.looprows:
            el.append(row.to_xml_element())

        return el


@dataclass
class Quota:
    """
    A <quota> element
    """
    label: str
    sheet: str
    content: str
    overquota: str = "noqual"


@dataclass
class GoTo:
    """ A <goto> element (skip logic) """
    target: str
    cond: Optional[str] = None


@dataclass
class Define:
    """_
    A <define> element (reusable list of rows)
    """
    label: str
    rows: Tuple["Row", ...] = ()


@dataclass
class Terminate:
    """ A <term> element (termination from survey)"""
    label: str
    cond: str
    content: str


@dataclass
class Logic:
    """ A <logic> node"""
    label: str
    uses: str
