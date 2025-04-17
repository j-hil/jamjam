"""Config file for the Sphinx documentation builder.

For the full list of built-in configuration values, see:
https://www.sphinx-doc.org/en/master/usage/configuration.html
"""

# -- Project information ---------------------------------- #
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "jamjam"
copyright = "2025, j-hil"
author = "j-hil"

# -- General configuration -------------------------------- #
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = ["sphinx.ext.autodoc"]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]


# -- Options for HTML output ------------------------------ #
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "alabaster"
html_static_path = ["_static"]
