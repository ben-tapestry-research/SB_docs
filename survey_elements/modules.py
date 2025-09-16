from dataclasses import dataclass
from survey_elements.models.structural import Block
from api.forsta_api_utils import download_project_file, fetch_modules
from survey_elements.parsing.xml_parser import parse_block

# Decipher project where <define> lists and text piping vars are held
DEPENDENCIES_PROJECT_CODE = "module_dependencies"


@dataclass()
class Module:
    title: str  # name of the module to show on-screen (e.g. CB: Category Brands)
    project_code: str  # Decipher project code (e.g. module_cb)
    main: Block  # The main module block where everything lives


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
