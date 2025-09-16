from api.forsta_api_utils import download_project_file
from api.forsta_api_utils import fetch_modules, format_fetched_modules
from survey_elements.parsing.xml_parser import parse_survey
from survey_elements.utils.xml_helpers import to_xml_string
from typing import Tuple, Any, Dict, List

modules: List[Dict[str, str]] = fetch_modules
modules_dict: Dict[str, str] = format_fetched_modules(modules = modules)

project_id = modules_dict.keys[0]

# Download (and save) the XML from Decipher
xml_root = download_project_file(f"/selfserve/2222/{project_id}", "xml")

# Parse into Python objects
survey: Tuple[Any] = parse_survey(xml_root)
example = survey[26]
type(example)
dir(example)
example.label
for eachthing in survey:
    print(to_xml_string(eachthing.to_xml_element(), pretty=True))