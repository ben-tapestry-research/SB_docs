from __future__ import annotations
from dataclasses import dataclass
from typing import TYPE_CHECKING, TypeAlias

from survey_elements.models.enums import Mode
from dataclasses import field

# Only import other package modules for type checking to avoid circular imports at runtime
if TYPE_CHECKING:
    from .logic import *
    from .questions import *


# Define the alias as a STRING so it’s not evaluated at runtime
BlockChild: TypeAlias = (
    "RadioQuestion | CheckboxQuestion | NumberQuestion | FloatQuestion | "
    "TextQuestion | TextAreaQuestion | SelectQuestion | Suspend | Exec | Note | "
    "Loop | Quota | GoTo | Define | Terminate | Block"
)



@dataclass(frozen=True)
class Note:
    content: str

@dataclass(frozen=True)
class Suspend:
    pass

@dataclass(frozen=True)
class Exec:
    content: str

@dataclass(frozen=True)
class Block:
    label: str | None = None
    children: tuple[BlockChild, ...] = ()

@dataclass(frozen=True)
class Res:
    label: str
    content: str

@dataclass
class Style:
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
    
