"""Configuration file for the Sphinx documentation builder.

For the full list of built-in configuration values, see the documentation:
https://www.sphinx-doc.org/en/master/usage/configuration.html

"""

import os
import sys
sys.path.insert(0, os.path.abspath('..'))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information
project = 'Residential Smart Grid Prototype'
copyright = '2025, Ez Aldin Waez; Abdullah Naal; Mohammad Labaniah; Abdo Kialy; Ruby Abbassy'
author = 'Ez Aldin Waez; Abdullah Naal; Mohammad Labaniah; Abdo Kialy; Ruby Abbassy'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinxcontrib.mermaid',
    'matplotlib.sphinxext.plot_directive',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# Language settings
language = os.environ.get('SPHINX_LANG', 'en')

# Internationalization settings
locale_dirs = ['_locale/']
gettext_compact = True
gettext_uuid = False

# Extensions configuration
autodoc_typehints = "description"

napoleon_attr_annotations = True
napoleon_include_special_with_doc = False
napoleon_include_private_with_doc = False

mermaid_output_format = 'svg'
mermaid_pdfcrop = 'pdfcrop'
mermaid_params = ['--theme', 'neutral']
mermaid_init_js = r"""
    mermaid.initialize({
        startOnLoad: true,
        theme: 'default',
        flowchart: {
            useMaxWidth: false,
            htmlLabels: true,
            curve: 'basis'
        },
        themeVariables: {
            fontSize: '14px'
        }
    });
"""

numfig = True


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output
html_title = project
html_short_title = project
html_theme = 'sphinx_book_theme'
html_static_path = ['_static']
html_use_index = True
html_domain_indices = True
html_theme_options = {
    'repository_url': 'https://github.com/ezAldinWaez/residential-smart-grid-prototype',
    'use_repository_button': True,
    'use_issues_button': False,
    'use_edit_page_button': False,
    'show_navbar_depth': 2,
    'show_toc_level': 2,
    'collapse_navigation': True,
    'navigation_depth': 3,
}
html_css_files = ['css/custom.css', 'css/rtl.css'] if language == 'ar' else ['css/custom.css']
html_js_files = ['js/rtl.js'] if language == 'ar' else []

# -- Options for LaTeX output ------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-latex-output
latex_engine = 'pdflatex'
latex_domain_indices = False
latex_show_pagerefs = True
latex_show_urls = 'footnote'
latex_documents = [(
    'index',  # startdocname
    'RSGP.tex',  # targetname
    'Residential Smart Grid Prototype',  # title
    'Ez Aldin Waez; Abdullah Naal; Mohammad Labaniah; Abdo Kialy; Ruby Abbassy',  # author
    'manual',  # theme
    True  # toctree_only
)]
latex_docclass = {'manual': 'book'}
latex_elements = {
    'papersize': 'a4paper',
    'pointsize': '12pt',
    'babel': '',
    'fncychap': r'''
        \usepackage[Rejne]{fncychap}
    ''',
    'preamble': r'''
        \usepackage{etoolbox}
    ''',
    'figure_align': 'H',
    'geometry': r'\usepackage{geometry} \geometry{outer=2.5cm}',
    'maketitle': r'''
        \pagenumbering{roman}

        \input{_titlepage.tex.txt}

        \cleardoublepage
        \phantomsection

        \input{_dedication.tex.txt}

        \cleardoublepage
        \phantomsection

        \input{_abstract.tex.txt}
    ''',
    'atendofbody': r'''
        \cleardoublepage
        \phantomsection
    ''',
    'tableofcontents': r'''
        \cleardoublepage
        \phantomsection

        \tableofcontents

        \cleardoublepage
        \phantomsection

        \listoffigures

        \cleardoublepage
        \phantomsection

        \listoftables

        \cleardoublepage
        \phantomsection

        \pagenumbering{arabic}
        \setcounter{page}{1}
    ''',
    'printindex': '',
}

latex_additional_files = [
    "_titlepage.tex.txt",
    "_abstract.tex.txt",
    "_dedication.tex.txt"
]
