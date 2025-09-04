from dataclasses import dataclass
from typing import Optional, Tuple
from question_elements import *
from structural_elements import *


@dataclass
class Loop:
    # A Loop can contain any question or structural element as a child.
    LoopChild = Union[
        "RadioQuestion", "CheckboxQuestion", "NumberQuestion", "TextQuestion",
        "TextAreaQuestion", "SelectQuestion", "Suspend", "Exec", "Note",
        "Loop", "Quota", "GoTo", "Define", "Terminate", "Block"
    ]
    children: tuple[LoopChild, ...] = ()


@dataclass
class Quota:
    """
    A <quota> element
    """
    label: str
    overquota: str = "noqual"
    sheet: str


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
    rows: Tuple[Row, ...] = ()


@dataclass
class Terminate:
    label: str
    cond: str

