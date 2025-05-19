# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
#
import os
import sys
from typing import Dict, Any

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))


# I've simplified this a little to use append instead of insert.
# sys.path.append(os.path.abspath('../../'))

# Specify settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'website.settings')

# Setup Django
import django
django.setup()

# ... leave the rest of conf.py unchanged


# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "LB2Observe"
copyright = "2024, Ob7"
author = "Adelphe N'Goran, Clémentine Violette, Pascal Cauquil, Julien Lebranchu"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    'sphinx.ext.napoleon',
    "sphinx.ext.doctest",
    "sphinx.ext.coverage",
    "sphinx.ext.duration",
    "sphinx.ext.intersphinx",
    "sphinx.ext.mathjax",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "sphinx.ext.githubpages",
    # "myst_nb",
    "myst_parser",
    "sphinx_design",
    # "notfound.extension",
    "sphinx_copybutton",
    "sphinx_codeautolink",
]

source_parsers = {
    '.md': 'recommonmark.parser.CommonMarkParser',
}
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}



# codeautolink
codeautolink_autodoc_inject = False
codeautolink_search_css_classes = ["highlight-default"]
codeautolink_concat_default = True

# ipython directive configuration
ipython_warning_is_error = False

# Copy plot options from Seaborn
# Include the example source for plots in API docs
plot_include_source = True
plot_formats = [("png", 90)]
plot_html_show_formats = False
plot_html_show_source_link = False

# Generate API documentation when building
autosummary_generate = True
numpydoc_show_class_members = False

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This patterns also effect to html_static_path and html_extra_path
exclude_patterns = ["_build", "build", "Thumbs.db", ".DS_Store", "notebooks/.ipynb_checkpoints"]
# configure notfound extension to not add any prefix to the urls
notfound_urls_prefix = "/en/latest/"



# # MyST related params
# nb_execution_mode = "auto"
# nb_execution_excludepatterns = ["*.ipynb"]
# nb_kernel_rgx_aliases = {".*": "python3"}
# myst_heading_anchors = 0
# myst_enable_extensions = ["colon_fence", "deflist", "dollarmath", "amsmath"]

# copybutton config: strip console characters
copybutton_prompt_text = r">>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
copybutton_prompt_is_regexp = True


# The base toctree document.
master_doc = "index"
default_role = "code"
suppress_warnings = ["mystnb.unknown_mime_type"]



# The name of the Pygments (syntax highlighting) style to use.
pygments_style = "sphinx"

# If true, `todo` and `todoList` produce output, else they produce nothing.
todo_include_todos = False

# -- Options for HTML output ----------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = "pydata_sphinx_theme"

# Theme options are theme-specific and customize the look and feel of a theme
# further.  For a list of options available for each theme, see the
# documentation.
html_theme_options = {
    "logo": {
        "image_light": "logo.png",
        # "image_dark": "logo_dark.png",
    },
    # https://pydata-sphinx-theme.readthedocs.io/en/stable/user_guide/header-links.html#fontawesome-icons
    "icon_links": [
        {
            "name": "GitHub",
            "url": "https://github.com/OB7-IRD/observe-logbooks-reader-webapp",
            "icon": "fa-brands fa-github",
        },
    ],
    "navbar_start": ["navbar-logo", "navbar-version"],
    "navbar_align": "content",
    "header_links_before_dropdown": 5,
    "secondary_sidebar_items": ["page-toc", "searchbox", "edit-this-page", "sourcelink"],
    "use_edit_page_button": True,
    # "analytics": {"google_analytics_id": "G-"},
    "external_links": [
        {"name": "The Ob7's team", "url": "https://ob7-ird.science"},
    ],
}
html_context = {
    "github_user": "OB7-IRD",
    "github_repo": "observe-logbooks-reader-webapp",
    "github_version": "main",
    "doc_path": "docs/source/",
    "default_mode": "light",
}
html_sidebars: Dict[str, Any] = {
    "index": [],
    "community": ["search-field.html", "sidebar-nav-bs.html"],
}

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
# html_theme_path = sphinx_bootstrap_theme.get_html_theme_path()
html_static_path = ["_static"]
html_css_files = ["custom.css"]

# use additional pages to add a 404 page
html_additional_pages = {
    "404": "404.html",
}

autodoc_mock_imports = ['django']

autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
}