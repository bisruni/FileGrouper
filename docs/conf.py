from __future__ import annotations

from datetime import datetime
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

project = "ArchiFlow"
author = "ArchiFlow Team"
copyright = f"{datetime.now().year}, {author}"
release = "1.0.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.autosummary",
    "sphinx_autodoc_typehints",
]

autosummary_generate = True
autodoc_member_order = "bysource"
autodoc_typehints = "description"
autodoc_typehints_format = "short"
always_document_param_types = True
autodoc_default_options = {
    "members": True,
    "undoc-members": True,
    "show-inheritance": True,
}
napoleon_google_docstring = True

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
language = "tr"

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
