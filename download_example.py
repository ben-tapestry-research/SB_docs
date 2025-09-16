import sys
from dotenv import load_dotenv

"""
sys.path.insert(1,r"C:\Users\GeorgePrice\git\SurveyBuilder\Survey-Builder")
load_dotenv(dotenv_path=r"C:\Users\GeorgePrice\git\SurveyBuilder\Survey-Builder\keys.env")
"""


from api.forsta_api_utils import download_project_file
from api.forsta_api_utils import fetch_modules, format_fetched_modules
from survey_elements.parsing.xml_parser import parse_survey
from survey_elements.models.structural import Block
from survey_elements.models.questions import Question
from survey_elements.utils.xml_helpers import to_xml_string
from typing import Tuple, Any, Dict, List



modules: List[Dict[str, str]] = fetch_modules()
modules_dict: Dict[str, str] = format_fetched_modules(modules = modules)

project_id: str = list(modules_dict.keys())[0]
project_id = "module_sm"
# Download (and save) the XML from Decipher
xml_root = download_project_file(f"/selfserve/2222/{project_id}", "xml")

# Parse into Python objects
survey: Tuple[Any] = parse_survey(xml_root)
len(survey)
# Identify Internal Questions
block = survey[22]
len(block.questions)
for question in block.questions:
    print(question.title)


questions = []
for attr in survey:
    if isinstance(attr, Block):
        questions = []

questions[3]
question_test = questions[3]
dir(question_test)
question_test.label

for eachthing in survey:
    print(to_xml_string(eachthing.to_xml_element(), pretty=True))