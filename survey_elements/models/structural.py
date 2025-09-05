from __future__ import annotations
from dataclasses import dataclass
from typing import Union, TYPE_CHECKING, TypeAlias

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