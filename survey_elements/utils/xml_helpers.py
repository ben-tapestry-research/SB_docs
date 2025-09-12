import xml.etree.ElementTree as ET


def _attr(el: ET, name: str, default="") -> str:
    """ Returns the value of a given attribute from an ElementTree

    Args:
        el (ET): The ElementTree object to search
        name (str): The name of the attribute to fetch
    Returns:
        str: The value of the attribute, or None if it does not exist
    """
    return el.attrib.get(name, default)


def _bit(el: ET, attr_name: str):  # returns bool | None
    """Helper function to return a boolean based upon attribute value
        e.g. randomize="0" --> False
             randomize="1" --> True

    Args:
        el (ET): The ElementTree object to work with
        attr_name (str): The name of the attribute to fetch (e.g. "randomize")

    Returns:
        bool | None: Boolean value or None
    """
    v = _attr(el, attr_name, None)
    if v is None:
        return None
    # Interpret as boolean
    return str(v).strip().lower() in {"1"}


def _tag_text(el: ET, tag: str) -> str:
    """Returns the text within a given tag, or None if the tag does not exist or has no text.

    Args:
        el (ET): The ElementTree object to search
        tag (str): The tag to search for

    Returns:
        str: The text within the tag, or None if the tag does not exist or has no text.
    """
    node = el.find(tag)
    return node.text if (node is not None and node.text is not None) else None


def _append_children(parent: ET.Element, children) -> None:
    """ 
    Append child elements to a parent XML element. Used in Question.to_xml_element() to add rows, cols, and choices.
        Args:
            parent (ET.Element): The parent XML element to which children will be appended.
            children (iterable): An iterable of child elements to append.
    """
    if not children:
        return
    for child in children:
        parent.append(child.to_xml_element())


def to_xml_string(el: ET.Element, pretty: bool = False) -> str:
    """ 
    Converts an ElementTree element back into an XML string
    Args:
        el (ET.Element): The ElementTree element to convert
        pretty (bool, optional): Whether to pretty-print the XML. Defaults to False.
        Returns:
        str: The XML string
    """
    xml_string = ET.tostring(el, encoding="unicode")
    if not pretty:
        return xml_string
    try:
        from xml.dom import minidom
        return minidom.parseString(xml_string).toprettyxml(indent="  ")
    except Exception:
        return xml_string

def _int_attr(el: ET.Element, name: str, default: int) -> int:
    """ Fetches an integer attribute from an ElementTree element, returning a default if not found or invalid
    We use this because ET.Element.get() returns str | None, and we want int with a default
    Args:
        el (ET.Element): The ElementTree object to search
        name (str): The name of the attribute to fetch
        default (int): The default value to return if the attribute is not found or invalid
        Returns:
        int: The integer value of the attribute, or the default"""
    raw = el.get(name)
    return int(raw) if raw is not None else default


def _parse_enum_set(el: ET.Element, attr_name: str, enum_class) -> set:
    """ 
    Parses a comma-separated list of enum values from an attribute into a set of enum members
    e.g. where="execute,survey"  -> {Where.EXECUTE, Where.SURVEY}
    Args:
        el (ET.Element): The ElementTree object to search
        attr_name (str): The name of the attribute to fetch
        enum_class: The Enum class to use for parsing (e.g. Where)
        Returns:
        set: A set of enum members
    """
    raw_text = _attr(el, attr_name, "")
    if not raw_text:
        return set()
    # Split up the comma-separated string into its parts
    parts = [p.strip() for p in raw_text.split(",") if p.strip()]
    vals = set()
    # where="execute,survey"  -> {Where("execute"), Where("survey")}
    for p in parts:
        try:
            vals.add(enum_class(p))
        except ValueError:
            raise ValueError(f"Invalid value for {attr_name}: '{p}'")
    return vals


def bool_bit(b: bool | None) -> str | None:
    """Get a string representation of a boolean value for XML attributes. (e.g. "1" or "0").

    Converts `True` to "1", `False` to "0", and `None` to `None`.

    Args:
        b (bool | None): The boolean value to convert.

    Returns:
        str | None: Returns "1" for `True`, "0" for `False`, and `None` for `None`.
    """
    return None if b is None else ("1" if b else "0")


def str_(s: object | None) -> str | None:
    """
Convert an object to a string for XML attributes. Used within the ATTR_MAP of dataclasses. We use this because the default str() function would convert None to "None", which we don't want in XML attributes.

    Args:
        s (object | None): The object to convert to a string.

    Returns:
        str | None: Returns `None` if the input is `None`, otherwise returns the string representation of the object.
    """
    return None if s is None else str(s)


def csv(xs) -> str | None:
    """Convert a collection of values to a comma-separated string for XML attributes. 
        Generally used for Enum sets, as the XML expects a comma-separated list of values.

    Args:
        xs (iterable): An iterable of values to convert.
    Returns:
        str | None: Returns a comma-separated string of sorted values, or `None` if the input is empty.
    """
    if not xs:
        return None
    # emit values; if enums, use .value
    vals = (getattr(x, "value", x) for x in xs)
    return ",".join(str(v) for v in sorted(vals))