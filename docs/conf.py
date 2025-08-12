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
    'sphinxcontrib.mermaid',
    'matplotlib.sphinxext.plot_directive',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Language settings
language = os.environ.get('SPHINX_LANG', 'en')

# Internationalization settings
locale_dirs = ['locale/']
gettext_compact = True
gettext_uuid = False

# Extensions configuration
autodoc_typehints = "description"

todo_include_todos = True

napoleon_attr_annotations = True
napoleon_include_special_with_doc = False
napoleon_include_private_with_doc = False

graphviz_output_format = 'png'
graphviz_dot_args = [
    '-Gfontname=Helvetica',
    '-Nfontname=Helvetica',
    '-Efontname=Helvetica',
]

mermaid_output_format = 'svg'
mermaid_pdfcrop = 'pdfcrop'

numfig = True


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
html_title = project
html_short_title = project
html_theme = 'sphinx_book_theme'
html_static_path = ['_static']
html_use_index = True
html_domain_indices = True

# Language switching context
html_context = {
    'languages': [
        ('en', 'English'),
        ('ar', 'العربية'),
    ],
    'current_language': language,
    'version_name': 'latest',
}
html_theme_options = {
    'repository_url': 'https://gitlab.com/ezAldinWaez/residential-smart-grid',
    'use_repository_button': True,
    'use_issues_button': False,
    'use_edit_page_button': False,
    'show_navbar_depth': 2,
    'show_toc_level': 2,
    'collapse_navigation': True,
    'navigation_depth': 3,
}

# -- Options for LaTeX output ------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-latex-output
latex_engine = 'pdflatex'
latex_logo = '_static/images/logo.png'
latex_domain_indices = False
latex_show_pagerefs = True
latex_show_urls = 'footnote'
latex_documents = [(
    'index',  # startdocname
    'RSG.tex',  # targetname
    'Residential Smart Grid',  # title
    'RSG Team',  # author
    'manual',  # theme
    True  # toctree_only
)]
latex_docclass = {'manual': 'book'}
latex_elements = {
    'papersize': 'a4paper',
    'pointsize': '12pt',
    'babel': '',
    'fontpkg': r'\usepackage{tgtermes} \usepackage{tgheros} \renewcommand\ttdefault{txtt}',
    # Some "fncychap" styles you can try are "Bjarne", "Sonny", "Lenny", "Glenn", "Conny", "Rejne" and "Bjornstrup". You can also set this to '' to disable fncychap.
    'fncychap': r'\usepackage[Rejne]{fncychap}',
    'preamble': r'\usepackage{custom_preamble}',
    'figure_align': 'H',
    'atendofbody': r'''''',
    'extraclassoptions': 'oneside,openany',
    'geometry': r'\usepackage{geometry} \geometry{outer=2.5cm}',
    'maketitle': r'''
        \pagenumbering{roman}

        \input{_titlepage.tex.txt}

        \cleardoublepage
        \phantomsection

        \input{_abstract.tex.txt}

        \cleardoublepage
        \phantomsection

        \input{_dedication.tex.txt}
    ''',
    'atendofbody': r'''''',
    'tableofcontents': r'''
        \cleardoublepage
        \phantomsection

        \tableofcontents

        \cleardoublepage
        \phantomsection

        \listoffigures

        \cleardoublepage
        \phantomsection

        \pagenumbering{arabic}
        \setcounter{page}{1}
    ''',
    'printindex': r'''
    ''',
}

latex_additional_files = [
    "custom_preamble.sty",
    "_titlepage.tex.txt",
    "_abstract.tex.txt",
    "_dedication.tex.txt"
]
