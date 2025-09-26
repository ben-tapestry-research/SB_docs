import sys
import os 
from tkinterdnd2 import TkinterDnD

from survey_builder import SurveyBuilderApp
from styles import configure_ttkbootstrap_styles

def main():
    """
    Main function to start the application.
    """
    # load .env (check to see if it is hardcoded, if not then should exist as .env in environment)

    root = TkinterDnD.Tk()

    configure_ttkbootstrap_styles(theme="flatly") # Sets our stylings app wide

    SurveyBuilderApp(master = root)



    # Run the Tkinter main loop
    root.mainloop()


if __name__ == '__main__':
    main()