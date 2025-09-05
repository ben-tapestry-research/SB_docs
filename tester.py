from pathlib import Path
from survey_elements.parsing.xml import parse_survey

xml_path = Path("example files") / "survey.xml"
elements = parse_survey(xml_path)