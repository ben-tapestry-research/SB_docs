# ------------- ENUMS (for attributes with specific allowable values) ------------- #

from enum import Enum


class Where(str, Enum):
    """
    Allowable values for the 'where' attribute in Element and Question classes.
    """
    EXECUTE = "execute"
    NOTDP = "notdp"
    NONE = "none"
    SUMMARY = "summary"
    SURVEY = "survey"
    REPORT = "report"
    DATA = "data"


class Grouping(str, Enum):
    """
    Allowable values for the 'grouping' attribute in Question class.
    """
    AUTO = "auto"
    ROWS = "rows"
    COLS = "cols"


class Legend(str, Enum):
    """
     Allowable values for the 'rowLegend' attribute in Question class.
    """
    DEFAULT = "default"
    BOTH = "both"
    LEFT = "left"
    RIGHT = "right"


class RowColChoiceShuffle(str, Enum):
    """
     Allowable values for the 'rowShuffle' and 'colShuffle' attributes in Question class.
    """
    FLIP = "flip"
    RFLIP = "rflip"
    ROTATE = "rotate"
    REVERSE_ROTATE = "reverse-rotate"
    RROTATE = "rrotate"


class Shuffle(str, Enum):
    """
     Allowable values for the 'shuffle' attribute in Question class.
     """
    NONE = "none"
    ROWS = "rows"
    COLS = "cols"
    CHOICES = "choices"


class Sort(str, Enum):
    """
     Allowable values for the 'sortChoices', 'sortCols', and 'sortRows' attributes in Question class."""
    NONE = "none"
    ASC = "asc"
    DESC = "DESC"
    SURVEY = "survey"
    REPORT = "report"

class Mode(str, Enum):
    """ Allowable values for the 'mode' attribute in <style> tags"""
    INSTEAD = "instead"
    BEFORE = "before"
    AFTER = "after"