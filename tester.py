from xml.etree import ElementTree as ET
from survey_elements import *


def test_basic_question():
    # build a RadioQuestion manually
    q = RadioQuestion(
        label="q1",
        title="Pick one",
        rows=(Row(label="r1", content="A"), Row(label="r2", content="B")),
    )
    print("Manual RadioQuestion:", q)


def test_parse_xml():
    xml = """
    <block label="b1">
      <note>Hello there</note>
      <radio label="q1" where="execute,survey,report">
        <title>Pick one</title>
        <row label="r1">A</row>
        <row label="r2">B</row>
      </radio>
      <loop label="loop1">
        <text label="t1" size="10">
          <title>Enter text</title>
        </text>
      </loop>
    </block>
    """
    root = ET.fromstring(xml)

    # parse into objects
    obj = element_from_xml_element(root)
    print("Parsed Block object:", obj)

    # confirm children types
    for child in obj.children:
        print(" Child:", type(child).__name__, getattr(child, "label", None))


def test_define_insert():
    xml = """
    <root>
      <define label="rows">
        <row label="r1">Apple</row>
        <row label="r2">Banana</row>
      </define>
      <block label="b1">
        <radio label="q1">
          <title>Fruit?</title>
          <insert label="rows"/>
        </radio>
      </block>
    </root>
    """
    root = ET.fromstring(xml)

    defines = find_defines(root)
    print(defines)
    exit()
    print("Defines found:", defines.keys())

    block = element_from_xml_element(root.find("block"))
    print("Block with inserted rows:", block)


if __name__ == "__main__":
    print("=== Basic Question ===")
    test_basic_question()

    print("\n=== Parse XML ===")
    test_parse_xml()

    print("\n=== Define/Insert ===")
    test_define_insert()
