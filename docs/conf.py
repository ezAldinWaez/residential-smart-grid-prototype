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
    'sphinx.ext.graphviz',
]

templates_path = ['_templates']
exclude_patterns = [
    '_build',
    'Thumbs.db',
    '.DS_Store'
]

# Graphviz configuration
graphviz_output_format = 'png'
graphviz_dot_args = [
    '-Gfontname=Helvetica',
    '-Nfontname=Helvetica',
    '-Efontname=Helvetica',
]

# Autodoc configuration
autodoc_typehints = "description"
todo_include_todos = True
napoleon_attr_annotations = True
napoleon_include_special_with_doc = False
napoleon_include_private_with_doc = False

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'  # you can try 'sphinx_book_theme'.
html_logo = '_static/images/logo.png'
html_static_path = ['_static']
html_css_files = ['custom.css']
html_use_index = False
html_domain_indices = False

# -- Options for LaTeX output ------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-latex-output

latex_engine = 'pdflatex'

latex_documents = [
    (
        'index',
        'ResidentialSmartGrid.tex',
        'Residential Smart Grid',
        'RSG Team',
        'manual'
    ),
]

latex_elements = {
    'papersize': 'a4paper',
    'pointsize': '12pt',
    'tableofcontents': '',
    'fontpkg': r'''
        \usepackage{helvet}
        \renewcommand{\familydefault}{\sfdefault}
    ''',
    'preamble': r'''
        \usepackage{etoolbox}
        \usepackage{titlesec}
        \usepackage[titles]{tocloft}
        \makeatletter
        \patchcmd{\@makechapterhead}{\thechapter\quad}{}{}{}
        \patchcmd{\tableofcontents}{\chapter*}{\section*}{}{}
        \patchcmd{\listoffigures}{\chapter*}{\section*}{}{}
        \patchcmd{\listoftables}{\chapter*}{\section*}{}{}
        \makeatother
    ''',
    'extraclassoptions': 'openany,oneside',
    'sphinxsetup': 'TitleColor={rgb}{0.126,0.263,0.361}, HeaderFamily=\\sffamily',
    'fncychap': r'\usepackage[Bjornstrup]{fncychap}',
    'printindex': r'\footnotesize\raggedright\printindex',

}

latex_domain_indices = False
