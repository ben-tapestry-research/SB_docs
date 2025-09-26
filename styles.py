"""
Module: styles.py
Description: Contains the app wide stylings along with theme choices

Attributes:
    THEMES: The styling theme options
    Fonts
    Buttons
    Labels
    Entry                     
"""
from tkinter import ttk
from ttkbootstrap.style import Style

# Define multiple themes
THEMES = {
    "standard": {
        "PRIMARY_COLOUR": "#28204D",
        "PRIMARY_COLOUR_LIGHTER" : "#3C3271",
        "ALTERNATE_COLOUR" : "#CB114F",
        "ALTERNATE_COLOUR_LIGHTER" : "#D7446F",
        "SPECIAL_COLOUR" : "#FAB619",
        "SPECIAL_COLOUR_DARKER": "#E0A217",
        "BACKGROUND_COLOUR": "#FFFFFF",
        "GREY_COLOUR" : "#808080",
        "GREY_COLOUR_LIGHTER" : "#696969",
        "LIGHT_COLOUR" : "white"   
        }
}

# Default Theme
CURRENT_THEME = THEMES["standard"]

# Fonts
FONT_FAMILY = "Century Gothic"
HEADER_FONT = (FONT_FAMILY, 25, "bold")
SUBHEADER_FONT = (FONT_FAMILY, 15, "bold")
SUBSUBHEADER_FONT = (FONT_FAMILY, 11, "bold")
LARGE_FONT = (FONT_FAMILY, 12)
MEDIUM_FONT = (FONT_FAMILY, 10)
SMALL_FONT = (FONT_FAMILY, 9)

#========================================================#
#============== ttkbootstrap styling ====================#
#========================================================#

def configure_ttkbootstrap_styles(theme="flatly"):
    style = Style(theme=theme)  # or "darkly", "flatly", "minty", etc.

    # Make sure the theme is properly activated
    style.theme_use(theme)

    # General font
    style.configure(".", font=MEDIUM_FONT, foreground=CURRENT_THEME['PRIMARY_COLOUR'])

    # main header
    style.configure("MainHeader.TLabel", 
        font=HEADER_FONT,
        foreground=CURRENT_THEME['PRIMARY_COLOUR'],
    )

    # title header
    style.configure("Title.TLabel", 
        font=HEADER_FONT,
        foreground=CURRENT_THEME['ALTERNATE_COLOUR'],
    )

    # sub header
    style.configure("SubHeader.TLabel", 
        font=SUBHEADER_FONT,
        foreground=CURRENT_THEME['PRIMARY_COLOUR'],
    )

    # subsub header
    style.configure("SubSubHeader.TLabel", 
        font=SUBSUBHEADER_FONT,
        foreground=CURRENT_THEME['PRIMARY_COLOUR'],
    )

    # subsub header (alternative)
    style.configure("SubSubHeaderAlternative.TLabel", 
        font=SUBSUBHEADER_FONT,
        foreground=CURRENT_THEME['ALTERNATE_COLOUR'],
    )

    # tooltip label
    style.configure("Tooltip.TLabel", # blue
        font=SMALL_FONT,
        foreground=CURRENT_THEME['PRIMARY_COLOUR']
    )

    # Primary/small buttons (dark purple)
    style.configure("primary.TButton", # blue
        font=MEDIUM_FONT,
        foreground=CURRENT_THEME['LIGHT_COLOUR'],
        background=CURRENT_THEME['PRIMARY_COLOUR'],
        borderwidth=0,
        padding=(10, 6),
        relief="flat"
    )
    style.map("primary.TButton",
        background=[("active", CURRENT_THEME['PRIMARY_COLOUR_LIGHTER']),("pressed", "#1E173D")])

    # alternate buttons (bold pink)
    style.configure("alternate.TButton",
        font=MEDIUM_FONT,
        background=CURRENT_THEME['ALTERNATE_COLOUR'],
        foreground=CURRENT_THEME['LIGHT_COLOUR'],
        borderwidth=0,
        padding=(12, 6)
    )
    style.map("alternate.TButton",
        background=[("active", CURRENT_THEME['ALTERNATE_COLOUR_LIGHTER']), ("pressed", "#A50C3F")]
    )

    # outline ghost (border) alternate button
    style.configure("AlternateGhost.TButton",
    font=SUBSUBHEADER_FONT,
    background=CURRENT_THEME['BACKGROUND_COLOUR'],
    foreground=CURRENT_THEME['ALTERNATE_COLOUR'],
    bordercolor=CURRENT_THEME['ALTERNATE_COLOUR'],
    borderwidth=1,
    relief="solid",
    padding=(10, 6)
    )
    style.map("AlternateGhost.TButton",
        background=[("active", CURRENT_THEME['BACKGROUND_COLOUR']), ("pressed", CURRENT_THEME['BACKGROUND_COLOUR'])],
        foreground=[("active", CURRENT_THEME['ALTERNATE_COLOUR_LIGHTER'])],
        bordercolor=[("active", CURRENT_THEME['ALTERNATE_COLOUR_LIGHTER']), ("pressed", "#1E173D")]
    )

    # special button (return)
    style.configure("special.TButton",
        font=MEDIUM_FONT,
        background=CURRENT_THEME['SPECIAL_COLOUR'],
        foreground=CURRENT_THEME['LIGHT_COLOUR'],
        borderwidth=0,
        padding=(12, 6)
    )
    style.map("special.TButton",
        background=[("active", CURRENT_THEME['SPECIAL_COLOUR_DARKER']), ("pressed", "#A67811")]
    )

    style.configure("grey.TButton",
        font=MEDIUM_FONT,
        background=CURRENT_THEME['GREY_COLOUR'],
        foreground=CURRENT_THEME['LIGHT_COLOUR'],
        borderwidth=0,
    )
    style.map("grey.TButton",
        background=[("active", CURRENT_THEME['GREY_COLOUR_LIGHTER']), ("pressed", "#A67811")]
    )

    style.configure("settings.TButton",
        font=MEDIUM_FONT,
        background=CURRENT_THEME['BACKGROUND_COLOUR'],
        foreground=CURRENT_THEME['LIGHT_COLOUR'],
        borderwidth=0,
    )
    style.map("settings.TButton",
        background=[("active", CURRENT_THEME['BACKGROUND_COLOUR']), ("pressed", CURRENT_THEME['BACKGROUND_COLOUR'])]
    )

    # Cancel button (return)
    style.configure("cancel.TButton",
        font=SUBSUBHEADER_FONT,
        background=CURRENT_THEME['BACKGROUND_COLOUR'],
        foreground=CURRENT_THEME['ALTERNATE_COLOUR'],
        borderwidth=0,
        padding=(12, 6)
    )
    style.map("cancel.TButton",
        foreground=[("active", CURRENT_THEME['ALTERNATE_COLOUR_LIGHTER']), ("pressed", CURRENT_THEME['ALTERNATE_COLOUR_LIGHTER'])],
        background=[("active", CURRENT_THEME['BACKGROUND_COLOUR']), ("pressed", CURRENT_THEME['BACKGROUND_COLOUR'])],
    )

    # Treeview headers
    style.configure("Treeview.Heading",
        background=CURRENT_THEME['PRIMARY_COLOUR'],
        foreground=CURRENT_THEME['LIGHT_COLOUR'],
        font=("Century Gothic", 9),
        padding=6
    )
    style.map("Treeview.Heading",
        background=[("active", CURRENT_THEME['PRIMARY_COLOUR_LIGHTER']), ("pressed", "#1E173D")]
    )
    style.map("Treeview",
          background=[("selected", "#e0e0e0")],
          foreground=[("selected", "#000000")]),
    
    
    # Sliding Scale #
    style.configure("Alternate.Horizontal.TScale", 
                    troughcolor=CURRENT_THEME['ALTERNATE_COLOUR'], 
                    sliderthickness=20,
    )


    # progress bar
    style.configure(
        "success.Horizontal.TProgressbar",
        background=CURRENT_THEME['ALTERNATE_COLOUR'],  
        thickness=16           
    )

    # Frame background override
    style.configure("TFrame",
        background=CURRENT_THEME['BACKGROUND_COLOUR']
    )

    #return style  # Optional: return it for reuse


# Styles
DEFAULT_BUTTON_STYLE = {
    "bg": CURRENT_THEME["PRIMARY_COLOUR"],
    "fg": "white",
    "padx": 10,
    "pady": 5
}

HOVER_BUTTON_STYLE = {
    "bg": CURRENT_THEME["PRIMARY_COLOUR_LIGHTER"],
}

GREY_BUTTON_STYLE = {
    "bg": CURRENT_THEME["GREY_COLOUR"],
    "fg": "white",
    "font" : (FONT_FAMILY, 10),
    "padx": 10,
    "pady": 5
}


HOVER_GREY_BUTTON_STYLE = {
    "bg": CURRENT_THEME["GREY_COLOUR_LIGHTER"],
}

STANDOUT_BUTTON_STYLE = {
    "bg" : CURRENT_THEME["ALTERNATE_COLOUR"],
    "fg" : "white",
    "font" : (FONT_FAMILY, 14),
    "padx": 10,
    "pady": 5
}

HOVER_STANDOUT_BUTTON_STYLE = {
    "bg" : CURRENT_THEME["ALTERNATE_COLOUR_LIGHTER"],
}

RETURN_BUTTON_STYLE = {
    "bg" : CURRENT_THEME["SPECIAL_COLOUR"],
    "fg" : "white",
    "font" : (FONT_FAMILY, 10),
    "padx": 10,
    "pady": 5
}

HOVER_RETURN_BUTTON_STYLE = {
    "bg" : CURRENT_THEME["SPECIAL_COLOUR_DARKER"],
}


# Extended Button Styles for Different Sizes
SMALL_BUTTON_STYLE = {**DEFAULT_BUTTON_STYLE, "font": SMALL_FONT}
MEDIUM_BUTTON_STYLE = {**DEFAULT_BUTTON_STYLE, "font": MEDIUM_FONT}
LARGE_BUTTON_STYLE = {**DEFAULT_BUTTON_STYLE, "font": LARGE_FONT}



LABEL_STYLE = {
    "font": LARGE_FONT,
    "bg": CURRENT_THEME["BACKGROUND_COLOUR"]
}

HEADER_STYLE = {
    "font": HEADER_FONT,
    "fg" : CURRENT_THEME["ALTERNATE_COLOUR"]
}

SUBHEADER_STYLE = {
    "font": SUBHEADER_FONT,
    "fg" : CURRENT_THEME["PRIMARY_COLOUR"]
}

SMALL_TEXT_STYLE = {
    "font": SMALL_FONT,
    "fg" : CURRENT_THEME["PRIMARY_COLOUR"]
}

SUBSUBHEADER_STYLE = {
    "font": SUBSUBHEADER_FONT,
    "fg" : CURRENT_THEME["PRIMARY_COLOUR"]
}

ENTRY_STYLE = {
    "font": MEDIUM_FONT
}

