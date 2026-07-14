# ruff: noqa
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import sys
from pathlib import Path

project = "libcst_code_mods"
copyright = "2026, Ed Cuss"
author = "Ed Cuss"
release = "2026"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

PROJECT_ROOT_DIR = Path(__file__).parents[2].resolve()
sys.path.insert(0, str(PROJECT_ROOT_DIR / "src"))


extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.coverage",
    "sphinx.ext.doctest",
    "sphinx.ext.napoleon",
    "sphinx.ext.githubpages",
]


templates_path = ["_templates"]
exclude_patterns = []
autodoc_default_options = {"members": True}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output


html_theme = "classic"
html_static_path = ["_static"]
