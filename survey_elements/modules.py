from dataclasses import dataclass
from survey_elements.models.structural import Block, HTML
from survey_elements.models.questions import Question
from survey_elements.models.logic import Loop, Define, Terminate

from api.forsta_api_utils import download_project_file, fetch_modules
from survey_elements.parsing.xml_parser import parse_block
from typing import Tuple, Iterator, List, Iterable, Any
# Decipher project where <define> lists and text piping vars are held
DEPENDENCIES_PROJECT_CODE = "module_dependencies"

@dataclass
class Module:
    title: str  # name of the module to show on-screen (e.g. CB: Category Brands)
    project_code: str  # Decipher project code (e.g. module_cb)
    main: Block  # The main module block where everything lives
    
    @property
    def editables(self) -> Tuple[Question, ...]:
        """
        Dynamic view of all Question instances inside this block.
        
        :return: Tuple of internal editable objects
        """
        return tuple(self._iter_editables_from([self.main]))

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

def load_module_from_project(project_path: str) -> Module:
    """
    Load a module from a Forsta project path (e.g. selfserve/2222/module_cb)
    
    Args:
        project_path (str): The Forsta project path (e.g. selfserve/2222/module_cb)
        Returns:
        Module: The loaded module
    """
    root = download_project_file(project_path, "xml", save_to_disk=False)

    # Fetch the lookup of project path --> survey name from Forsta API
    lookup_dict = fetch_modules()
    project_name = lookup_dict.get(project_path)
    if project_name is None:
        raise ValueError(
            f"Project path: {project_path} not found in fetch_modules() dict"
        )
    final_name = project_name.replace("[MODULES] ", "")
    print(final_name)

    main_block = root.find(
        "block"
    )  # top-level <block> tag of the survey is all the module
    main = parse_block(main_block)

    return Module(title=final_name, project_code=project_path, main=main)
