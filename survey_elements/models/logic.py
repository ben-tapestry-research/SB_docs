from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, Tuple, TypeAlias


# Only import types at type-check time to avoid runtime circular imports
if TYPE_CHECKING:
    from .questions import *
    from .structural import *

@dataclass
class Loopvar:
    name: str
    value: str | None = None

@dataclass
class Looprow:
    label: str | None = None
    vars: tuple[Loopvar, ...] = ()


# Define the alias as a STRING so it’s not evaluated at runtime
LoopChild: TypeAlias = (
    "RadioQuestion | CheckboxQuestion | NumberQuestion | FloatQuestion | "
    "TextQuestion | TextAreaQuestion | SelectQuestion | Suspend | Exec | Note | "
    "Loop | Quota | GoTo | Define | Terminate | Block"
)


@dataclass
class Loop:
    # A Loop can contain any question or structural element as a child.#
    label: str
    children: tuple[LoopChild, ...] = ()
    looprows: tuple[Looprow, ...] = ()


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
    target: str


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

