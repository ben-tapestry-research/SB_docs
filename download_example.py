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

module3.HTMLs

survey.add(module1)
survey.add(module2)
survey.add(module3)

# Example of Define Manipulation
survey.required_defines_labels
question = survey.questions[94] # This question has 'Brands' DefineRef

survey.create_define("BRANDS", ["Ikea", "Kellogs", "Simpsons"])
survey.created_defines

survey.resolve_inserts()
question.define_refs[1].parent_list()

# Example of Question Manipulation
question2 = survey.questions[3] # question is 'Which gender do you identify as?'
question2.editable = True # Set the editable to true
# For the sake of example I am going to create my editabe regions
question2.title = r"Which {{gender}} do you {{identify as}}?"
# Create my editable question template
question2._set_editable_template() # This is done on question innit but have to rerun as we have changed manually the title
question2.editable_obj
question2.editable_obj.editables # shows me I can edit 'gender' and 'identify as'
question2.editable_obj.set_value("gender", "genders")
question2.editable_obj.set_value("identify as", "belong to")
question2.render_question()
question2.title # Which genders do you belong to


# Exmaple of Survey Manipulation
survey.module_titles
survey.swap(0,1)
survey.reorder(project_code_order = ("module_sm", "module_xc"))

for question in survey.get("module_sm").questions:
    print(question.title)