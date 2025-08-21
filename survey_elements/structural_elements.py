from dataclasses import dataclass
from typing import Union
from question_elements import *
from logic_elements import *


@dataclass(frozen=True)
class Note:
    content = str


@dataclass(frozen=True)
class Suspend:
    pass


@dataclass(frozen=True)
class Exec:
    content = str


@dataclass(frozen=True)
class Block:
    label: str
    # Allowable child elements of Block
    BlockChild = Union[
        "RadioQuestion", "CheckboxQuestion", "NumberQuestion", "TextQuestion",
        "TextAreaQuestion", "SelectQuestion", "Suspend", "Exec", "Note",
        "Loop", "Quota", "GoTo", "Define", "Terminate", "Block"
    ]
    children: tuple[BlockChild, ...] = ()
