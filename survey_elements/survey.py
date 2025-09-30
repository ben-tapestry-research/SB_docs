"""
Handles survey organisation


Author: George
Date: September 2025
"""

from dataclasses import dataclass, field
from functools import cached_property
from typing import Set, Tuple, Iterator, List, Sequence, Optional, Dict, Any
from survey_elements.modules import Module, Editable
from survey_elements.models.questions import Question, Row
from survey_elements.models.logic import Define, DefineRef
from survey_elements.models.structural import HTML

@dataclass
class Survey:
    """
    Data structure for an entire survey


    """

    title: str
    survey_id: str

    comments: Optional[str] = None

    modules: List[Module] = field(default_factory=list)

    user_defines: Dict[str, Define] = field(default_factory = dict) # user created defines (from UI)

    # Labels of the defines where the user needs to fill in the info for them
    ROW_PREFIXES: dict[str, str] = field(
        default_factory=lambda: {
            "FREQUENCY": "fr",
            "FREQUENCY_SHORT": "frs",
            "CONSIDERATION": "con",
            "RECENCY": "rec",
            "CATEGORIES": "cat",
            "BRANDS": "br",
            "PRIORITY_LEVEL_LISTS": "pll",
            "PERCEPTIONS": "per",
            "MOTIVATIONS": "mot",
            "CATEGORY_ATTITUDES": "ca",
            "LIFE_ATTITUDES": "la",
            "LQ_CHEM": "lqc",
            "LQ_EMOT": "lqe",
            "LQ_RATIONAL": "lqr",
            "LQ_COMPAT": "lqco",
            "MESSAGES": "msg",
            "STREAMINGBRANDS": "stb",
            "SOCIALMEDIA": "sm",
            "NEWSPAPERS": "np",
            "MAGAZINES": "mag",
            "AUDIOSTREAMINGBRANDS": "asb",
            "RADIOSTATIONS": "rs",
            "WEBSITES": "web",
            "SHOWS": "sh",
            "CHANNELS": "ch",
            "MEDIA": "med",
            "INTERESTS": "int",
            "SPORTS": "spo",
        },
        init=False,
        repr=False,
    )

    @property
    def module_titles(self) -> Tuple[str]:
        """Returns names of internal modules"""
        return tuple(m.title for m in self.modules)

    @property
    def editables(self) -> Tuple[Editable, ...]:
        """
        Returns all editable classes within its current modules

        :return: Tuple of internal editable objects
        """
        return tuple(e for m in self.modules for e in m.editables)

    @property
    def objects(self) -> Tuple[Any, ...]:
        """
        View of all internal objects inside all internal modules
        :return: Tuple of all internal objects
        """
        # TODO Consider making this a @cached_property
        return tuple(o for m in self.modules for o in m.objects)

    @property
    def questions(self) -> Tuple[Question, ...]:
        return tuple(q for m in self.modules for q in m.questions)

    @property
    def HTMLs(self) -> Tuple[HTML, ...]:
        return tuple(h for m in self.modules for h in m.HTMLs)

    @property
    def defines(self) -> Tuple[Define, ...]:
        return tuple(d for m in self.modules for d in m.defines)
    
    @property
    def required_defines_sources(self) -> Set[str]:
        """ Set of the sources (labels) for all the required defines in the child modules"""
        return {d for m in self.modules for d in m.required_define_sources}
 
    @property
    def define_refs(self) -> Tuple[DefineRef, ...]:
        """ Tuple of all instances of DefineRefs in survey """
        return tuple(d for m in self.modules for d in m.define_refs)
    
    # TODO Create a mapping dictionary for its modules and its modules contents
    @property
    def map(self) -> Dict[str, Any]:
        """Create a mapping dictionary of its modules and child classes"""
        pass

    @property
    def ordered(self) -> Tuple[Module, ...]:
        """Tuple view of modules in order."""
        return tuple(self.modules)

    # -- Module Functions -- #
    def __len__(self) -> int:
        return len(self.modules)

    def __iter__(self) -> Iterator[Module]:
        return iter(self.modules)

    def __getitem__(self, idx: int) -> Module:
        return self.modules[idx]

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
        """Returns true if module already entered"""
        return any(m.project_code == project_code for m in self.modules)

    def add(self, module: Module) -> None:
        """Append a module to the end; enforces unique project_code."""
        if self.dup_check(module.project_code):
            raise ValueError(f"Duplicate project_code '{module.project_code}'")
        # Reset cached properties
        if hasattr(self, "invalidate_cache"):
            self.invalidate_cache()
        self.modules.append(module)

    def insert(self, index: int, module: Module) -> None:
        """Insert a module at a specific index; enforces unique project_code."""
        if self.dup_check(module.project_code):
            raise ValueError(f"Duplicate project_code '{module.project_code}'")
        # Reset cached properties
        if hasattr(self, "invalidate_cache"):
            self.invalidate_cache()
        self.modules.insert(index, module)

    def remove_at(self, index: int) -> Module:
        """Remove and return the module at index."""
        # Reset cached properties
        if hasattr(self, "invalidate_cache"):
            self.invalidate_cache()
        return self.modules.pop(index)

    def remove(self, project_code: str) -> Module:
        """Remove and return the module identified by project_code."""
        idx = self.index_of(project_code)
        # Reset cached properties
        if hasattr(self, "invalidate_cache"):
            self.invalidate_cache()
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
        self.modules[index_a], self.modules[index_b] = (
            self.modules[index_b],
            self.modules[index_a],
        )

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
                new_list.append(code_to_mod.pop(code))  # get and remove Module
            except KeyError:
                raise ValueError(f"Unknown project_code in reorder: '{code}'")
        if code_to_mod:
            missing = ", ".join(code_to_mod.keys())
            raise ValueError(f"Reorder is missing module(s): {missing}")
        self.modules = new_list

    def create_define(self, def_label: str, items: List[str]) -> None:
        """Create or replace an editable Define object with the given label and items."""
        if def_label not in self.required_defines_sources:
            raise ValueError(
                f"Define with label {def_label} not in required defines for survey"
            )
        if def_label not in self.ROW_PREFIXES:
            raise ValueError(f"Define label {def_label} is not editable via create_define()")

        # build rows into a list, then convert to tuple for Define
        def_rows_list: List[Row] = []
        prefix = self.ROW_PREFIXES[def_label]

        # Row labels in define will be prefix + ascending counter (e.g. fs1, fs2, etc...)
        for idx, each_content in enumerate(items, start=1):
            def_rows_list.append(Row(label=f"{prefix}{idx}", content=each_content))
        def_rows = tuple(def_rows_list)

        final_define = Define(label=def_label, rows=def_rows)
        # Add to created_define dict
        self.user_defines[def_label] = final_define

    # TODO This is not the best way to do this but it works for now
    def resolve_inserts(self) -> None:
        """
        Replace DefineRef placeholders in queestion.rows with the rows from the corresponding Define.
        Needs to be called after all modules are loaded into the survey
        """
        for question in self.questions:
            insert_rows = []
            for ref in question.define_refs:
                label = ref.source
                if label in self.ROW_PREFIXES:
                    define_insert = self.user_defines.get(label, None)
                    if not define_insert:
                        raise ValueError(f"Define {label} was not created")
                    insert_rows.append(define_insert.rows)
            if insert_rows:
                # Log DefineRefs before resolve
                if not question.historic_define_refs:
                    question.historic_define_refs = question.define_refs
                # Resolve Rows
                question.rows = tuple(insert_rows)

    def invalidate_cache(self, cascade: bool = True, *names: str) -> None:
        """
        Invalidate this Survey's caches
        Optionally cascade to modules.
        
        :param cascade: If true, trigger invalidate_cache in modules
        :param names: Names of properties to invalidate
        """
        if not names:
            names = () # names of @cached_property properties

        for name in names:
            self.__dict__.pop(name, None)
        
        if cascade:
            for m in self.modules:
                if hasattr(m, "invalidate_cache"):
                    m.invalidate_cache(*names)
    '''
    def list_defines(self) -> dict:
        """Return a mapping define_label -> source.
          - 'survey'  -> survey._defines (created/imported into survey)
          - 'editable:[module]' -> editable define present in a module (should be at survey-level)
          - 'module:[module]' -> non-editable define found in module
        """
        mapping: dict[str, str] = {}
        # survey-owned defines first
        for d in self._defines:
            mapping[d.label] = "survey"

        # module defines: if editable label not in survey._defines show it as editable:<module>
        for m in self.modules:
            mod_name = getattr(m, "title", None) or getattr(m, "project_code", "<unknown>")
            for d in getattr(m, "defines", ()):
                if d.label in mapping:
                    continue  # already recorded as survey-owned
                if d.label in self.ROW_PREFIXES:
                    mapping[d.label] = f"editable:{mod_name}"
                else:
                    mapping[d.label] = f"module:{mod_name}"
        return mapping
    '''
