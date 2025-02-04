# pylint: disable=locally-disabled, invalid-name, redefined-builtin

"""Configuration file for the Sphinx documentation builder.

For the full list of built-in configuration values, see the documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html

"""

import os
import sys
sys.path.insert(0, os.path.abspath('..'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Residential Smart Grid'
copyright = '2025, RSG Team'
author = 'RSG Team'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.todo',
    'sphinx_rtd_dark_mode',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

todo_include_todos = True
napoleon_attr_annotations = True
napoleon_include_special_with_doc = False
napoleon_include_private_with_doc = False
default_dark_mode = False

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_logo = '_static/logo.jpg'
html_css_files = ['custom.css']

# -- Options for LaTeX output ------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-latex-output

latex_elements = {
    'papersize': 'a4paper',
    'pointsize': '12pt',
    'fontpkg': r"""
        \PassOptionsToPackage{bookmarksnumbered}{hyperref}
    """,
    'preamble': r"""
        \usepackage{setspace}
    """,
    'maketitle': r"""
        \pagenumbering{arabic}
    """,
}
