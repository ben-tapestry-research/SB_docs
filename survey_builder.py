# tkinter #
import tkinter as tk
from tkinter import ttk, simpledialog
from typing import List, Dict, Set, Optional
import ttkbootstrap as tb
from api.forsta_api_utils import fetch_modules
import sys
from dotenv import load_dotenv


class ModuleSelector(tk.Frame):
    """
    Single module selection box with an 'upload' button.
    
    
    """
    def __init__(self, parent, module_list: List[str], on_remove: Optional[callable]=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.on_remove = on_remove
        self.module_name = tk.StringVar(value="")
        self.module_list = ['Module1', "Module2", "Module3"]

        # Main box styling
        self.config(relief="groove", bd=2, padx=10, pady=10)

        # Upload button
        self.select_btn = ttk.Button(self, 
                                     text="Select Module", 
                                     command=lambda: self.select_module(module_list), 
                                     style = "alternate.TButton")
        self.select_btn.pack()

        # Label to show selected module
        self.label = ttk.Label(self, textvariable=self.module_name, style = "SubSubHeaderAlternative.TLabel")
        self.label.bind("<Button-1>", lambda e: self.module_info(self.module_name))
        self.label.pack(pady=5)


    def select_module(self, module_list: List[str]) -> None:
        """
        Select a module from a listbox of available modules

        :param module_list: The list of available modules
        """
        def on_submit():
            """ Handles module selection submission """
            # Add selected module
            sel = module_lb.curselection()
            if not sel:  # nothing selected
                print("No module selected")
                return
            
            choice = module_lb.get(sel)
            self.module_name.set(choice)
            self.select_btn.pack_forget() # hide upload button
            window.destroy()  # Close the dialog after selection

        parent = self.winfo_toplevel()
        window = tk.Toplevel(parent)
        window.title("Select Module")
        window.transient(parent)
        window.grab_set()
        window.resizable(False, False)
        window.focus_force()
        ttk.Label(window, text="Select a module:").pack(padx=10, pady=10)

        # Single-selection mode using Listbox
        module_lb = tk.Listbox(
            window,
            selectmode=tk.SINGLE,
            exportselection=False,
            font=('Century Gothic', 8),
            height=min(12, max(4, len(module_list)))
        )

        for module in module_list:
            module_lb.insert(tk.END, module)
        module_lb.pack(padx=10, pady=10)

        tb.Button(window, text="Submit", command=on_submit, style = "primary.TButton").pack(pady=5)
        module_lb.bind("<Double-1>", on_submit)
        window.bind("<Return>", on_submit)
        window.bind("<Escape>", lambda e: window.destroy())

        window.wait_window()  # Wait for the dialog to close before continuing

    def module_info(self, module_name: str):
        """
        Opens pop-up window with information on the module
        """
        if not module_name:
            # No module selected
            return
        info_window = tk.Toplevel(self)
        info_window.title(module_name)
        info_window.transient(self)
        info_window.grab_set()

        info_frame = tk.Frame(info_window)
        info_frame.pack(pady=10,padx = 10)
        






class ModuleList(tk.Frame):
    """Container for multiple ModuleSelectors with add button and scroll support."""
    def __init__(self, parent, module_list: List[str],**kwargs):
        super().__init__(parent, **kwargs)
        self.module_list = module_list
        # Scrollable canvas
        canvas = tk.Canvas(self, borderwidth=0)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Add button at bottom
        self.add_button = ttk.Button(self.scrollable_frame, text="+ Add Module", command=self.add_module_box)
        self.add_button.pack(pady=5)

        # Add first empty box
        self.add_module_box()

    def add_module_box(self):
        """Add a new ModuleSelector box."""
        module_box = ModuleSelector(self.scrollable_frame, module_list=self.module_list)
        module_box.pack(fill="x", pady=5, padx=5, before=self.add_button)


class SurveyBuilderApp(tk.Frame):
    """

    """
    def __init__(self, 
                 master: tk.Frame, 
                 ):
        """
        
        """
        super().__init__(master)  # Ensure tk.Frame is initialized with the master
        self._app_class = self.__class__
        intermediatory = SurveyBuilderIntermediatory
        self.grid(row=0, column=0, sticky="nsew")
        # Header
        title = ttk.Label(self, text="Survey Builder", style = "MainHeader.TLabel")
        title.grid(row=1, column=0, columnspan=3, pady=10, sticky="n")


        sys.path.insert(1,r"C:\Users\GeorgePrice\git\SurveyBuilder\Survey-Builder")
        load_dotenv(dotenv_path=r"C:\Users\GeorgePrice\git\SurveyBuilder\Survey-Builder\keys.env")


        # TODO Should be in a front-end class
        modules_dict = fetch_modules() # Connect to forsta API
        module_titles = [modules_dict[m].title for m in modules_dict.keys]

        print(modules_dict)
        modules_frame = tk.Frame(self)
        modules_frame.grid(row = 2, column = 0)
        module_list = ModuleList(modules_frame, module_titles)
        module_list.pack(fill="both", expand=True, padx=10, pady=10)


class SurveyBuilderIntermediatory:
    """
    Handles interactions between the SurveyBuilder backend structure and the frontend
    """
    modules_dict = fetch_modules()
    
    @property
    def module_titles(self):
        return [self.modules_dict[m].title for m in self.modules_dict.keys]
    
    @property
    def module_paths(self):
        return [self.modules_dict[m].project_path for m in self.modules_dict.keys]
