"""Regular expressions"""

from __future__ import annotations
import re

HTML_DIRECTIVE = re.compile(
    r"(html|def) (.*)(?:\(|\(.*?\))(?:\))?(?:\:)?"
)  # simplify this abomination
HTML_IMPORT = re.compile(r"from (.*) import html (.*)")
HTML_ELEMENT = re.compile(r"<.*>\n*.*\n*.*<\/.*>")
COMPONENTS = None


def component_regex(functions: list[str]):
    return re.compile(
        rf"<(?:{'|'.join(functions)}).*>\n*.*\n*.*<\/(?:{'|'.join(functions)})>"
    )
