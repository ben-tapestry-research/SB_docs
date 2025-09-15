from api.forsta_api_utils import download_project_file
from survey_elements.parsing.xml_parser import parse_survey
project_id = "module_sm"

# Download (and save) the XML from Decipher
xml_root = download_project_file(f"/selfserve/2222/{project_id}", "xml")

# Parse into Python objects
survey = parse_survey(xml_root)