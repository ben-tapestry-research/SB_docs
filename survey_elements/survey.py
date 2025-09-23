"""
Handles survey organisation


Author: George
Date: September 2025
"""

from dataclasses import dataclass, field
from typing import Set, Tuple, Iterator, List, Sequence, Optional, Dict, Any
from survey_elements.modules import Module, Editable
from survey_elements.models.logic import Define
from survey_elements.models.questions import Question
from survey_elements.models.logic import Loop, Define, Terminate
from survey_elements.parsing.xml_parser import required_defines

@dataclass
class Survey:
    """
    Data structure for an entire survey
    
    
    """
    title: str
    survey_id: str

    comments: Optional[str] = None

    modules: List[Module] = field(default_factory=list)

    required_defines: Set[str] = field(default_factory=set)

    @property
    def module_titles(self) -> Tuple[str]:
        """ Returns names of internal modules """
        return tuple(m.title for m in self.modules)

    @property
    def editables(self) -> Tuple[Editable, ...]:
        """
        Returns all editable classes within its current modules
        
        :return: Tuple of internal editable objects
        """
        return tuple(e for m in self.modules for e in m.editables)

    @property
    def questions(self) -> Tuple[Question, ...]:
        return tuple(q for m in self.modules for q in m.questions)

    @property
    def defines(self) -> Tuple[Define, ...]:
        return tuple(d for m in self.modules for d in m.defines)

    # TODO Create a mapping dictionary for its modules and its modules contents 
    @property
    def map(self) -> Dict[str, Any]:
        """ Create a mapping dictionary of its modules and child classes """
        pass

    # -- Module Functions -- #
    def __len__(self) -> int:
        return len(self.modules)

    def __iter__(self) -> Iterator[Module]:
        return iter(self.modules)

    def __getitem__(self, idx: int) -> Module:
        return self.modules[idx]

    @property
    def ordered(self) -> Tuple[Module, ...]:
        """Tuple view of modules in order."""
        return tuple(self.modules)

    def index_of(self, project_code: str) -> int:
        """Find the index of a module by project_code; raises ValueError if not found."""
        for i, m in enumerate(self.modules):
            if m.project_code == project_code:
                return i
        raise ValueError(f"Module with project_code='{project_code}' not found")

    def get(self, project_code: str) -> Module:
        """Get a module by project_code; raises ValueError if not found."""
        return self.modules[self.index_of(project_code)]

    def dup_check(self, project_code: str) -> bool:
        """ Returns true if module already entered """
        return any(m.project_code == project_code for m in self.modules)

    def add(self, module: Module) -> None:
        """Append a module to the end; enforces unique project_code."""
        if self.dup_check(module.project_code):
            raise ValueError(f"Duplicate project_code '{module.project_code}'")
        self.modules.append(module)

        # incorporate inserts referenced while parsing this mo
        defines = required_defines()
        self.required_defines.update(defines)

    def insert(self, index: int, module: Module) -> None:
        """Insert a module at a specific index; enforces unique project_code."""
        if self.dup_check(module.project_code):
            raise ValueError(f"Duplicate project_code '{module.project_code}'")
        self.modules.insert(index, module)

    def remove_at(self, index: int) -> Module:
        """Remove and return the module at index."""
        return self.modules.pop(index)

    def remove(self, project_code: str) -> Module:
        """Remove and return the module identified by project_code."""
        idx = self.index_of(project_code)
        return self.modules.pop(idx)

    def move(self, old_index: int, new_index: int) -> None:
        """
        Move module from old_index to new_index
        Example: move(5, 0) brings item at 5 to the front.
        """
        mod = self.modules.pop(old_index)
        self.modules.insert(new_index, mod)

    def move_by_code(self, project_code: str, new_index: int) -> None:
        """Move a given module to new_index."""
        self.move(self.index_of(project_code), new_index)

    def swap(self, index_a: int, index_b: int) -> None:
        """Swap two modules by index."""
        self.modules[index_a], self.modules[index_b] = self.modules[index_b], self.modules[index_a]

    def reorder(self, project_code_order: Sequence[str]) -> None:
        """
        Reorder modules to match the given sequence of project_codes exactly.
        All modules must be present and unique in the provided order.
        """
        if len(project_code_order) == 1 or len(self.modules) == 1:
            # reorder pointless
            return

        code_to_mod = {m.project_code: m for m in self.modules}
        new_list: List[Module] = []
        for code in project_code_order:
            try:
                new_list.append(code_to_mod.pop(code)) # get and remove Module
            except KeyError:
                raise ValueError(f"Unknown project_code in reorder: '{code}'")
        if code_to_mod:
            missing = ", ".join(code_to_mod.keys())
            raise ValueError(f"Reorder is missing module(s): {missing}")
        self.modules = new_list
