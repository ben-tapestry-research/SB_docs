from pathlib import Path
from survey_elements.parsing.xml import parse_survey
from survey_elements.utils.xml_helpers import to_xml_string

xml_path = Path("example files") / "survey.xml"
elements = parse_survey(xml_path)

print(elements[0])

print(to_xml_string(elements[0].to_xml_element()))