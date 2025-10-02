"""
Handles module organisation such as the Module dataclass and loading modules from API


Author: George
Date: September 2025
"""

from xml.etree import ElementTree as ET
from dataclasses import dataclass, field
from survey_elements.models.structural import Block, HTML
from survey_elements.models.questions import Question
from survey_elements.models.logic import Loop, Define, DefineRef, Terminate
from api.forsta_api_utils import download_project_file
from survey_elements.parsing.xml_parser import parse_block
from typing import Tuple, Iterator, List, Iterable, Any, TypeAlias, Set, Callable
from pathlib import Path
from functools import cached_property

# Decipher project where <define> lists and text piping vars are held
DEPENDENCIES_PROJECT_CODE = "module_dependencies"

Editable: TypeAlias = "Question | Define | Terminate | HTML"

@dataclass
class Module:
    """
    Data structure for a survey module
    
    """
    title: str  # name of the module to show on-screen (e.g. "CB: Category Brands")
    project_path: Path # Path for project (e.g. Path("selfserve/2222/module_sm"))
    main: Block  # The main module block where everything lives

    editable_types = (Question, Define, Terminate, HTML)

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
    def project_code(self) -> str:
        # Decipher project code (e.g. "module_cb")
        return self.project_path.name

    @property
    def editables(self) -> Tuple[Editable, ...]:
        """
        Dynamic view of all editable classes inside this module.
        
        :return: Tuple of internal editable objects
        """
        return tuple(self._iter_objects_from([self.main], self.editable_types))

    @property
    def objects(self) -> Tuple[Any, ...]:
        """
        View of all internal objects inside this module
        
        :return: Tuple of all internal objects
        """
        return tuple(self._iter_objects_from([self.main], None))

    @property
    def questions(self) -> Tuple[Question, ...]:
        return self._filter_objects(Question)

    @property
    def defines(self) -> Tuple[Define, ...]:
        return self._filter_objects(Define)
    
    @property
    def define_refs(self) -> Tuple[DefineRef, ...]:
        """ Tuple of all DefineRef instances in this modules questions """
        return tuple(ref for q in self.questions for ref in getattr(q, "define_refs", ()))

    @property
    def required_define_sources(self) -> Set[str]:
        """
        Set of the 'source' of all the required define lists
        Obtained via define_refs (which is obtained via questions) so is dynamic depending
            on child questions
        """
        return {d.source for d in self.define_refs if d.source in self.ROW_PREFIXES}

    @property
    def HTMLs(self) -> Tuple[HTML, ...]:
        return self._filter_objects(HTML)

    @property
    def terminates(self) -> Tuple[Terminate, ...]:
        return self._filter_objects(Terminate)
    
    def _iter_objects_from(self, nodes: Iterable[Any], types: Tuple[Any]) -> Iterator[Question]:
        """
        Yields all internal objects.
        Recurses into any node that has a `.children` attribute (Blocks, Loops, etc.).

        Yielded objects are limited to selected types (Question, Define etc.).

        :param nodes: The nodes to search through
        :param types: The types of object you want to yield
        """
        for node in nodes:
            # If node is of selected type object, yield it
            if types:
                # Type has been specified
                if isinstance(node, types):
                    yield node
            else:
                # Type irrelevent
                yield node

            # If node has children (Block, Loop, etc.), recurse into container
            children = getattr(node, "children", None)
            if children:
                # children may be tuple/list of mixed nodes (questions, blocks, loops, etc.)
                yield from self._iter_objects_from(children, types)

    def _filter_objects(self, *types: Any) -> Tuple[Any, ...]:
        """Filter the objects tuple by isinstance against provided types."""
        return tuple(e for e in self.objects if isinstance(e, types))

    def invalidate_cache(self, *names: str) -> None:
        """
        Invaidates cached properties after any structural changes (i.e. question deletion)
        """
        if not names:
            names = () # names of @cached_property properties
        for n in names:
            self.__dict__.pop(n, None)

    def delete_object(self, target: Any) -> int:
        """
        Delete all occurrences of this object from the module tree.
        
        :param target: The object to delete
        :return removed: The number of removed instances of the object
        """
        self.main, removed = _prune_children(self.main, match=lambda x: x is target)
        # Reset cached properties
        if hasattr(self, "invalidate_cache"):
            self.invalidate_cache()
        return removed
    
    # TODO Currently just deletes the question class, does not delete associated objects such as suspends, execs etc.
    def delete_question_by_title(self, title: str) -> int:
        """
        Delete all Questions with matching title attribute.
        
        :param title: The title of the question to delete
        :return removed: The number of removed instances of the question
        """
        def _match(x: object) -> bool:
            return isinstance(x, Question) and getattr(x, "title", None) == title

        self.main, removed = _prune_children(self.main, match=_match)
        # Reset cached properties
        if hasattr(self, "invalidate_cache"):
            self.invalidate_cache()
        return removed
    
    def to_xml_element(self) -> ET.Element:
        """Converts the module to an ElementTree object

        Returns:
            ET.Element: The Module represented as an ElementTree
        """
        module_children = self.main.children
        print(f"Module {self.project_code} has {len(module_children)} child elements")

        # Create the <block label="module_xx"> ... </block> wrapper
        root = ET.Element("block", {"label": self.project_code})
        
        for obj in module_children:
            if hasattr(obj, "to_xml_element"):
                child = obj.to_xml_element()
                root.append(child)
            else:
                raise TypeError(f"{obj} has no to_xml_element() method")
    
        return root


def _prune_children(node, match: Callable[[object], bool]) -> tuple[object, int]:
    """
    Remove any child (recursively) for which match(child) is True.
    Returns (possibly mutated node, total_removed).

    :param node: The starting node to recursively prune
    :param match: The match function to decide whether to remove
    :return node: A potentially modified new node with the desired objects removed
    :return removed: The number of removed objects
    """
    removed = 0
    children = getattr(node, "children", None)
    if not children:
        return node, 0

    new_children = []
    for ch in children:
        if match(ch):
            removed += 1
            continue
        if isinstance(ch, (Block, Loop)):
            ch, r = _prune_children(ch, match)
            removed += r
        new_children.append(ch)

    # replace children (Block/Loop assumed mutable; children is a tuple)
    if removed:
        node.children = tuple(new_children)
    return node, removed

def load_module_from_project(module_title: str, project_path: str, save_to_disk=False) -> Module:
    """
    Load a module from a Forsta project path (e.g. selfserve/2222/module_cb)
    
    :param module_title: The name of the module (e.g. CB: Category Brands)
    :param project_path: The Forsta project path (e.g. selfserve/2222/module_cb)
    :return: The initiated Module
    """
    if not isinstance(project_path, str):
        raise TypeError("Ensure 'project_path' is a str type")    
    if not isinstance(module_title, str):
        raise TypeError("Ensure 'module_title' is a str")
    print("here2")
    root = download_project_file(project_path, "xml", save_to_disk=save_to_disk)
    print("here3")
    main_block = root.find(
        "block"
    )  # top-level <block> tag of the survey is all the module
    main = parse_block(main_block)

    return Module(title=module_title, project_path=Path(project_path), main=main)


