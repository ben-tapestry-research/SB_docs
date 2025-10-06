# # docs/conf.py
# extensions = [
#     "myst_parser",          # allow Markdown-like features in reST if wanted
#     "sphinx.ext.graphviz",  # for the import graph (optional; requires Graphviz)
# ]
# myst_enable_extensions = ["colon_fence"]  # lets you use ::: fenced blocks if you want
# html_theme = "furo"
# templates_path = ["_templates"]
# html_static_path = ["_static"]
# exclude_patterns = []
# project = "Survey Builder"
# # optional (crisper diagrams):
# graphviz_output_format = "svg"


import os, sys
# Make both repo-root and src/ layouts work:
for p in ("..", "../src"):
    full = os.path.abspath(p)
    if os.path.isdir(full) and full not in sys.path:
        sys.path.insert(0, full)

extensions = [
    "myst_parser",
    "sphinx.ext.autodoc",          # renders docstrings
    "sphinx.ext.autosummary",      # optional: summary tables
    "sphinx.ext.napoleon",         # Google/NumPy docstrings
    "sphinx.ext.viewcode",         # [source] links
]
autosummary_generate = True
autodoc_member_order = "bysource"      # keep your code order
autodoc_default_options = {
    "members": True,
    "undoc-members": False,       # don’t show undocumented
    "inherited-members": False,   # don’t pull in base-class stuff
    "private-members": False,     # don’t show _private
    "show-inheritance": True,
}
# If imports fail due to heavy deps, mock them here:
# autodoc_mock_imports = ["pandas", "numpy", "requests"]

html_theme = "furo"
project = "Survey Builder"
myst_enable_extensions = ["colon_fence"]

extensions += ["sphinx.ext.intersphinx"]
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", {}),
    # add libraries you reference, e.g.:
    # "requests": ("https://requests.readthedocs.io/en/latest/", {}),
}