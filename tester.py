from survey_elements.question_elements import *


def to_xml_string(el: ET.Element, pretty: bool = False) -> str:
    xml = ET.tostring(el, encoding="unicode")
    if not pretty:
        return xml
    try:
        from xml.dom import minidom
        return minidom.parseString(xml).toprettyxml(indent="  ")
    except Exception:
        return xml


# Example usage
rq = RadioQuestion(
    label="q1",
    title="xx",
    comment="${res.SP1}",
    rows=(Row(label="r1", content="hello"), Row(label="r2", content="hello2")),
)

print(to_xml_string(rq.to_xml_element(), pretty=True))
