"""
Handles module organisation such as the Module dataclass and loading modules from API


Author: George
Date: September 2025
"""

from dataclasses import dataclass
from survey_elements.models.structural import Block, HTML
from survey_elements.models.questions import Question
from survey_elements.models.logic import Loop, Define, Terminate
from api.forsta_api_utils import download_project_file
from survey_elements.parsing.xml_parser import parse_block
from typing import Tuple, Iterator, List, Iterable, Any, TypeAlias
from pathlib import Path
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
        return tuple(self._iter_editables_from([self.main]))

    @property
    def questions(self) -> Tuple[Question, ...]:
        return self._filter_editables(Question)

    @property
    def defines(self) -> Tuple[Define, ...]:
        return self._filter_editables(Define)
    
    @property
    def HTMLs(self) -> Tuple[HTML, ...]:
        return self._filter_editables(HTML)

    @property
    def terminates(self) -> Tuple[Terminate, ...]:
        return self._filter_editables(Terminate)
    
    def _iter_editables_from(self, nodes: Iterable[Any]) -> Iterator[Question]:
        """
        Yields user-editable objects.
        Recurses into any node that has a `.children` attribute (Blocks, Loops, etc.).

        Yielded objects are limited to `Editable` types (Question, Define etc.).

        :param nodes: The nodes to search through
        """
        editable_types = (Question, Define, Terminate, HTML)

        for node in nodes:
            # If node is an editable object, yield it
            if isinstance(node, editable_types):
                yield node

            # If node has children (Block, Loop, etc.), recurse into container
            children = getattr(node, "children", None)
            if children:
                # children may be tuple/list of mixed nodes (questions, blocks, loops, etc.)
                yield from self._iter_editables_from(children)

    def _filter_editables(self, *types: Any) -> Tuple[Any, ...]:
        """Filter the editables tuple by isinstance against provided types."""
        return tuple(e for e in self.editables if isinstance(e, types))
    

def load_module_from_project(module_title: str, project_path: str) -> Module:
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

    root = download_project_file(project_path, "xml", save_to_disk=False)
    main_block = root.find(
        "block"
    )  # top-level <block> tag of the survey is all the module
    main = parse_block(main_block)

    return Module(title=module_title, project_path=Path(project_path), main=main)
