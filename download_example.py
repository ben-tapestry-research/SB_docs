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

# Look at structure of survey
for object in survey.objects:
    print(object.__class__.__name__)

# Example of Question Deletion
# TODO At the moment it just deletes the question object, however, deletion of a question could also require deletion of
#       other objects - therefore, these other objects need to be linked to the Question Object so we know to delete them
#       as well
for question in module1.questions:
    question.label
question_to_delete = module1.questions[2]
module1.delete_object(question_to_delete)
for question in survey.questions:
    question.label

# Example of Define Manipulation
survey.required_defines_sources # Need to create a 'BRANDS' list
survey.get("module_cb").questions[28] # This question has 'Brands' DefineRef

survey.create_define("BRANDS", ["Ikea", "Kellogs", "Simpsons"])
survey.user_defines # stored here
survey.resolve_inserts() # resolves 

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

# Can also do HTML #
HTML1 = survey.HTMLs[0]
HTML1.editable = True # Set the editable to true
HTML1.content = r"{{Thanks}}! \n<br /><br />\nIn this section we {{look}} at different [pipe: ORG]."
HTML1._set_editable_template()
HTML1.editable_obj.editables
HTML1.editable_obj.set_value("Thanks", "Not thanks")
HTML1.editable_obj.set_value("look", "view")
HTML1.editable_obj.render()
HTML1.render_content()
HTML1.content

# Exmaple of Module Manipulation
survey.module_titles
survey.swap(0,1)
survey.reorder(project_code_order = ("module_sm", "module_xc"))

for question in survey.get("module_sm").questions:
    print(question.title)