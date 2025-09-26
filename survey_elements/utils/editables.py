"""
Name: editables.py
Author: George
Date: September 2025

Classes to allow for user manipulation and change within our structural classes

Classes:
    FixedText: Token class for fixed text
    EditableText: Token class for editable text
    EditableTemplate: Stores editable text and splits into Fixed and Editable allowing for user manipulation
"""
from typing import Optional, Union, Callable, List, Dict
from dataclasses import dataclass, field
import re

@dataclass
class FixedText:
    text: str

@dataclass
class EditableText:
    """ 
    Editable token of an editable text 
    
    Allows for custom validation of changes
    """
    name: str
    value: str = ""
    context: Optional[str] = None # The entire text for use in validation
    validator: Optional[Callable[[str], bool]] = None
    error: Optional[str] = None

    def set(self, new_value: str) -> None:
        if self.validator and not self.validator(new_value):
            self.error = f"Invalid value for '{self.name}'."
        else:
            self.value = new_value
            self.error = None

Token = Union[str, EditableText]

@dataclass
class EditableTemplate:
    """ 
    Class to store an editable text 

    Allows for multiple sections of a question to be editable
    
    """
    raw_template: str
    
    start: str = "{"
    end: str = "}"
    tokens: List[Token] = field(init=False)

    def __post_init__(self):
        """ Split on initiation """
        self.tokens = self._split_template()

    @property
    def raw_text(self):
        """ The raw text without start and end signifiers"""
        return re.sub(r'[{start}{end}]', '', self.raw_template)

    def _split_template(self) -> List[Token]:
        """Split raw_template into FixedText and EditableText tokens."""
        pattern: str = re.escape(self.start) + r"(.*?)" + re.escape(self.end)
        parts: List[str ]= re.split(pattern, self.raw_template)

        tokens: List[Token] = []
        # Odd indexes are editable, even are fixed
        for i, part in enumerate(parts):
            if i % 2 == 0:  # fixed
                if part:
                    tokens.append(FixedText(part))
            else:  # editable
                tokens.append(EditableText(name = part.strip(), context = self.raw_text))
        return tokens

    @property
    def editables(self) -> Dict[str, EditableText]:
        """ The editable tokens """
        return {t.name: t for t in self.tokens if isinstance(t, EditableText)}

    def set_value(self, name: str, value: str) -> None:
        """ Change editable token """
        if name in self.editables:
            self.editables[name].value = value

    def render(self) -> str:
        """ Render question with edits """
        out = []
        for t in self.tokens:
            out.append(t.text if isinstance(t, FixedText) else t.value or f"{self.start}{t.name}{self.end}")
        return "".join(out)
    
