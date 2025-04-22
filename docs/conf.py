"""Config file for the Sphinx documentation builder.

For the full list of built-in configuration values, see:
https://www.sphinx-doc.org/en/master/usage/configuration.html

Good examples of documentation setup:
* Basic use:
    - https://github.com/more-itertools/more-itertools/tree/master
    - https://github.com/pypa/packaging/tree/main
    - https://github.com/python-attrs/attrs
* Uses ``sphinx.ext.apidoc``:
    - https://github.com/pytroll/satpy/tree/main
"""

# https://www.sphinx-doc.org/en/master/usage/configuration
#
project = "jamjam"
copyright = "2025, j-hil"
author = "j-hil"
extensions = ["sphinx.ext.autodoc", "sphinx.ext.apidoc"]
templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
html_theme = "furo"
html_title = "JamJam"
html_static_path = ["_static"]
html_favicon = "favicon.xml"

# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html#configuration
#
autodoc_member_order = "bysource"
autodoc_preserve_defaults = True
autodoc_typehints = "signature"
autodoc_type_aliases = {"Fn": "jamjam.typing.Fn"}

# https://www.sphinx-doc.org/en/master/usage/extensions/apidoc.html
#
apidoc_modules = [
    {"path": "../jamjam/", "destination": "api/"}
]
apidoc_exclude_patterns = ["**/test*"]
apidoc_max_depth = 0
apidoc_separate_modules = True
apidoc_module_first = True
