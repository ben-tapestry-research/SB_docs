"""
Logic elements for survey XML structure.

Classes:
    Loopvar: Represents a <loopvar> element within a looprow.
    Looprow: Represents a <looprow> element within a loop.
    Loop: Represents a <loop> element containing questions and structural elements.
    Quota: Represents a <quota> element for managing survey quotas.
    GoTo: Represents a <goto> element for skip logic.
    Define: Represents a <define> element for reusable rows.
    Terminate: Represents a <terminate> element for ending the survey.
    Logic: Represents a <logic> element for survey logic definitions.
    SampleSources: Represents a <samplesources> element containing multiple <samplesource> elements.
    SampleSource: Represents a <samplesource> element defining a sample source.
    Var: Represents a <var> element within a <samplesource>.
    Exit: Represents an <exit> element within a <samplesource>.
    Condition: Represents a <condition> element for conditional logic.

Methods:
    to_xml_element() -> ET.Element: Convert to an XML element

Author: Ben Andrews
Date: August 2025
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, Tuple, TypeAlias, Iterator
from xml.etree import ElementTree as ET

# Only import types at type-check time to avoid runtime circular imports
if TYPE_CHECKING:
    from .questions import *
    from .structural import *
else:
    Block = None

@dataclass
class Loopvar:
    """
    A <loopvar> element (within a looprow)
    https://forstasurveys.zendesk.com/hc/en-us/articles/4409477040667-Loop-Tag-Cycle-Through-Questions

    Methods:
        to_xml_element() -> ET.Element: Convert to an XML element
    """

    name: str
    value: str | None = None

    def to_xml_element(self) -> ET.Element:
        """Convert to an XML element"""
        attr = {"name": self.name}
        el = ET.Element("loopvar", attr)
        el.text = self.value
        return el


@dataclass
class Looprow:
    """
    A <looprow> element (within a loop)
    https://forstasurveys.zendesk.com/hc/en-us/articles/4409477040667-Loop-Tag-Cycle-Through-Questions

    Methods:
        to_xml_element() -> ET.Element: Convert to an XML element
    """

    label: str
    cond: str | None = None
    vars: tuple[Loopvar, ...] = ()

    def to_xml_element(self) -> ET.Element:
        """Convert to an XML element"""
        attrs = {"label": self.label}

        if self.cond not in [None, ""]:
            attrs["cond"] = self.cond

        el = ET.Element("looprow", attrs)

        for loopvar in self.vars:
            child = loopvar.to_xml_element()
            el.append(child)

        return el


@dataclass
class Loop:
    """
    A <loop> element
    https://forstasurveys.zendesk.com/hc/en-us/articles/4409477040667-Loop-Tag-Cycle-Through-Questions

    Methods:
        to_xml_element() -> ET.Element: Convert to an XML element
    """

    label: str

    # A Loop can contain any question or structural element as a child.
    # Define the alias as a string - avoids weird runtime issues I was getting
    LoopChild: TypeAlias = (
        "RadioQuestion | CheckboxQuestion | NumberQuestion | FloatQuestion | "
        "TextQuestion | TextAreaQuestion | SelectQuestion | Suspend | Exec | Note | "
        "Loop | Quota | GoTo | Define | Terminate | Block"
    )
    children: tuple[LoopChild, ...] = ()
    looprows: tuple[Looprow, ...] = ()

    @property
    def questions(self) -> Tuple[Question, ...]:
        """
        Dynamic view of all Question instances inside this loop.
        
        :return: Tuple of internal questions
        """
        return tuple(self._iter_questions())

    def _iter_questions(self) -> Iterator[Question]:
        """
        Yield Question objects from children.
        If nested Block or Loop, delve into it to retrieve questions
        """
        from .questions import Question
        from .structural import Block # local import avoids circular import at module load
        for child in self.children:
            if isinstance(child, Question):
                yield child
            elif isinstance(child, (Block, Loop)):
                yield from child._iter_questions()

    def to_xml_element(self) -> ET.Element:
        """Convert to an XML element"""
        attrs = {"label": self.label}
        el = ET.Element("loop", attrs)

        for child in self.children:
            # Raise error if child of loop has no to_xml_element method
            try:
                el.append(child.to_xml_element())
            except Exception as e:
                raise TypeError(
                    f"Child of Loop has no to_xml_element method: {child}"
                ) from e

        for row in self.looprows:
            el.append(row.to_xml_element())

        return el


@dataclass
class Quota:
    """
    A <quota> element
    https://forstasurveys.zendesk.com/hc/en-us/articles/10100597040795-Adding-Quotas-Using-the-XML-Editor#2.3
    """

    label: str
    sheet: str
    content: str
    overquota: str = "noqual"

    def to_xml_element(self) -> ET.Element:
        """Convert to an XML element"""
        attrs = {"label": self.label, "sheet": self.sheet, "overquota": self.overquota}
        el = ET.Element("quota", attrs)
        el.text = self.content
        return el


@dataclass
class GoTo:
    """
    A <goto> element (skip logic)
    https://forstasurveys.zendesk.com/hc/en-us/articles/4409469858715-Goto-Tag-Jump-to-a-Different-Section

    Methods:
        to_xml_element() -> ET.Element: Convert to an XML element
    """

    target: str
    cond: Optional[str] = None

    def to_xml_element(self) -> ET.Element:
        """Convert to an XML element"""
        attrs = {"target": self.target}
        if self.cond not in [None, ""]:
            attrs["cond"] = self.cond

        el = ET.Element("goto", attrs)
        return el


@dataclass
class Define:
    """_
    A <define> element (reusable list of rows)

    https://forstasurveys.zendesk.com/hc/en-us/articles/4409461496347-Reusable-Answer-List-Element#_2:_Adding_a_Reusable_Answer_List_in_the_XML_Editor

    Methods:
        to_xml_element() -> ET.Element: Convert to an XML element
    """

    label: str
    rows: Tuple["Row", ...] = ()

    def to_xml_element(self) -> ET.Element:
        """Convert to an XML element"""
        attrs = {"label": self.label}
        el = ET.Element("define", attrs)

        for row in self.rows:
            el.append(row.to_xml_element())

        return el


@dataclass
class Terminate:
    """
    A <term> element (termination from survey)
    https://forstasurveys.zendesk.com/hc/en-us/articles/4409469883931-Term-Tag-Terminate-Screen-Out-Participants

    Methods:
        to_xml_element() -> ET.Element: Convert to an XML element
    """

    label: str
    cond: str
    content: str

    def to_xml_element(self) -> ET.Element:
        """Convert to an XML element"""
        attrs = {"label": self.label, "cond": self.cond}
        el = ET.Element("terminate", attrs)
        el.text = self.content
        return el


@dataclass
class Logic:
    """
    A <logic> node
    https://forstasurveys.zendesk.com/hc/en-us/articles/4417353772187-Adding-Logic-Nodes-Using-the-XML-Editor

    Methods:
        to_xml_element() -> ET.Element: Convert to an XML element
    """

    label: str
    uses: str

    def to_xml_element(self) -> ET.Element:
        """Convert to an XML element"""
        attrs = {"label": self.label, "uses": self.uses}
        el = ET.Element("logic", attrs)
        return el


@dataclass
class SampleSources:
    """
    A <samplesource> node (that contains <samplesource> elements)
    https://forstasurveys.zendesk.com/hc/en-us/articles/4409461305883-Configuring-Participant-Sources

    Methods:
        to_xml_element() -> ET.Element: Convert to an XML element

    """

    default: str
    samplesources: tuple[SampleSource, ...] = ()

    def to_xml_element(self) -> ET.Element:
        """Convert to an XML element"""
        attrs = {"default": self.default}
        el = ET.Element("samplesources", attrs)

        for ss in self.samplesources:
            el.append(ss.to_xml_element())

        return el


@dataclass
class SampleSource:
    """
    A <samplesource> node
    https://forstasurveys.zendesk.com/hc/en-us/articles/4409461305883-Configuring-Participant-Sources

    Methods:
        to_xml_element() -> ET.Element: Convert to an XML element
    """

    list: str
    title: str
    invalid: str
    completed: str
    vars: tuple[Var, ...] = ()
    exits: tuple[Exit, ...] = ()

    def to_xml_element(self) -> ET.Element:
        """Convert to an XML element"""
        attrs = {
            "list": self.list,
            "title": self.title,
            "invalid": self.invalid,
            "completed": self.completed,
        }
        el = ET.Element("samplesource", attrs)

        # <samplesource> can contain multiple <var> and <exit> elements
        for var in self.vars:
            el.append(var.to_xml_element())

        for exit_var in self.exits:
            el.append(exit_var.to_xml_element())

        return el


@dataclass
class Var:
    """
    A <var> node (within a <samplesource>)
    https://forstasurveys.zendesk.com/hc/en-us/articles/4409461305883-Configuring-Participant-Sources

    Methods:
        to_xml_element() -> ET.Element: Convert to an XML element
    """

    name: str
    unique: str
    values: str

    def to_xml_element(self) -> ET.Element:
        """Convert to an XML element"""
        attrs = {"name": self.name, "unique": self.unique, "values": self.values}
        el = ET.Element("var", attrs)
        return el


@dataclass
class Exit:
    """
    An <exit> node (within a <samplesource>)
    https://forstasurveys.zendesk.com/hc/en-us/articles/4409461305883-Configuring-Participant-Sources

    Methods:
        to_xml_element() -> ET.Element: Convert to an XML element
    """

    cond: str
    url: str | None = None
    content: str | None = None

    def to_xml_element(self) -> ET.Element:
        """Convert to an XML element"""
        attrs = {"cond": self.cond}
        if self.url not in [None, ""]:
            attrs["url"] = self.url

        el = ET.Element("exit", attrs)
        el.text = self.content
        return el


@dataclass
class Condition:
    """
    A <condition> tag
    https://forstasurveys.zendesk.com/hc/en-us/articles/4409461304859-Condition-Tag-Create-Simpler-References-to-Condition-Logic

    Methods:
        to_xml_element() -> ET.Element: Convert to an XML element
    """

    label: str
    cond: str
    content: str

    def to_xml_element(self) -> ET.Element:
        """Convert to an XML element"""
        attrs = {"label": self.label, "cond": self.cond}
        el = ET.Element("condition", attrs)
        el.text = self.content
        return el
