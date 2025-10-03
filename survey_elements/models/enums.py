"""
Enums for survey elements. Defines allowable values for various attributes in Element and Question attributes.
(e.g. where="execute,survey,report", etc...)

Allows for better type checking and validation. Used to convert comma-separated strings into lists of enum values and vice versa.

Author: Ben Andrews
Date: July 2025
"""

from enum import Enum


class Where(str, Enum):
    """
    Allowable values for the 'where' attribute in Element and Question classes.
    The where attribute specifies if the element or question should be included in the survey / data exports

    https://forstasurveys.zendesk.com/hc/en-us/articles/4409476917915-Control-where-an-Element-Appears-with-the-Where-Attribute
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

    The grouping attribute controls how the question's <row> and <column> elements are grouped.
    For example, when grouped by rows, then answers are selected on a per-row basis.
    When grouped by columns, selections are made on a per column basis

    https://forstasurveys.zendesk.com/hc/en-us/articles/4409469872411-Question-Attributes
    """

    AUTO = "auto"
    ROWS = "rows"
    COLS = "cols"


class Legend(str, Enum):
    """
     Allowable values for the 'rowLegend' attribute in Question class.

     By default, row legends are displayed on the left. If rowLegend="both" is specified, then the row text will appear on both sides
     Used in 'this or that' polar questions

    https://forstasurveys.zendesk.com/hc/en-us/articles/4409469872411-Question-Attributes
    """

    DEFAULT = "default"
    BOTH = "both"
    LEFT = "left"
    RIGHT = "right"


class RowColChoiceShuffle(str, Enum):
    """
    Allowable values for the 'rowShuffle' and 'colShuffle' attributes in Question class.

    Specify the randomization order of <row> elements
    https://forstasurveys.zendesk.com/hc/en-us/articles/4409469872411-Question-Attributes
    """

    FLIP = "flip"
    RFLIP = "rflip"
    ROTATE = "rotate"
    REVERSE_ROTATE = "reverse-rotate"
    RROTATE = "rrotate"


class Shuffle(str, Enum):
    """
    Allowable values for the 'shuffle' attribute in Question class.

    Which of the question's elements to randomize
    https://forstasurveys.zendesk.com/hc/en-us/articles/4409469872411-Question-Attributes
    """

    NONE = "none"
    ROWS = "rows"
    COLS = "cols"
    CHOICES = "choices"


class Sort(str, Enum):
    """
    Allowable values for the 'sortChoices', 'sortCols', and 'sortRows' attributes in Question class.

    https://forstasurveys.zendesk.com/hc/en-us/articles/4409469872411-Question-Attributes
    """

    NONE = "none"
    ASC = "asc"
    DESC = "DESC"
    SURVEY = "survey"
    REPORT = "report"


class Mode(str, Enum):
    """
    Allowable values for the 'mode' attribute in <style> tags

    https://forstasurveys.zendesk.com/hc/en-us/articles/4409461374491-XML-Style-System
    """

    INSTEAD = "instead"
    BEFORE = "before"
    AFTER = "after"

class ViewMode(str, Enum):
    """ 
    Allowable values for the atm1d:viewMode attribute for a question
    https://forstasurveys.zendesk.com/hc/en-us/articles/4409461312923-Customizing-the-Button-Select-Element
    
    """
    VERTICAL = "vertical"
    TILED = "Tiled"
    HORIZONTAL = "Horizontal"

class Align(str, Enum):
    """ 
    Allowable values for the atm1d:buttonAlign/contentAlign attributes for a question
    https://forstasurveys.zendesk.com/hc/en-us/articles/4409461312923-Customizing-the-Button-Select-Element
    
    """
    LEFT = "Left"
    CENTER = "Center"
    RIGHT = "Right"