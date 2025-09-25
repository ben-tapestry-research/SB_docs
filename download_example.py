import sys
from dotenv import load_dotenv


sys.path.insert(1,r"C:\Users\GeorgePrice\git\SurveyBuilder\Survey-Builder")
load_dotenv(dotenv_path=r"C:\Users\GeorgePrice\git\SurveyBuilder\Survey-Builder\keys.env")



from api.forsta_api_utils import fetch_modules
from survey_elements.models.questions import Question
from survey_elements.modules import Module, load_module_from_project
from survey_elements.survey import Survey
from pathlib import Path
from typing import Dict

modules: Dict[str, Dict[str, str]] = fetch_modules()

survey = Survey(title = "Test Survey", survey_id = "test")
module1: Module = load_module_from_project(module_title = "SM: Core Screening", project_path = "selfserve/2222/module_sm")
module2: Module = load_module_from_project(module_title = "XC: Core Demographics", project_path = "selfserve/2222/module_xc")
module3: Module = load_module_from_project(module_title = "BP: Brand Perception", project_path = "selfserve/2222/module_cb")

survey.add(module1)
survey.add(module2)
survey.add(module3)

len(module3.questions)

question = module3.questions[28]

question.rows

for question in module3.questions:
    question.rows


# The required defines for the survey - de-duped set of LABELS from <insert> tags
defines_needed = survey.required_defines

for label in defines_needed:
    # TODO: editable define = user needs to add rows via front-end
    if label in survey.ROW_PREFIXES:
        survey.create_define(label, ["row content 1 from front-end", "row content 2 from front-end"])
    else:
        print(f"non-editable define found: {label}")

for label, src in survey.list_defines().items():
    print(label, "=>", src)

# Function to resolve inserts found in a survey (where <insert> tags are, we map them back to the rows of the corresponding <define>)
# maybe could be helpful later in the front-end?
survey.resolve_inserts()



survey.module_titles
survey.swap(0,1)
survey.reorder(project_code_order = ("module_sm", "module_xc"))

for question in survey.get("module_sm").questions:
    print(question.title)