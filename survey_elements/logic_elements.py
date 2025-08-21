from dataclasses import dataclass
from question_elements import *
from structural_elements import *


@dataclass(frozen=True)
class Loop:
    LoopChild = Union[
        "RadioQuestion", "CheckboxQuestion", "NumberQuestion", "TextQuestion",
        "TextAreaQuestion", "SelectQuestion", "Suspend", "Exec", "Note",
        "Loop", "Quota", "GoTo", "Define", "Terminate", "Block"
    ]
    children: tuple[LoopChild, ...] = ()


@dataclass(frozen=True)
class Quota:
    label: str
    overquota: str = "noqual"
    sheet: str


@dataclass(frozen=True)
class GoTo:
    target = "str"
    cond: Optional[str] = None


@dataclass(frozen=True)
class Define:
    label: str
    rows: Tuple[Row, ...] = ()


@dataclass(frozen=True)
class Terminate:
    label: str
    cond: str
