"""Regular expressions"""

from __future__ import annotations
import re

HTML_DIRECTIVE = re.compile(
    r"(html|def) (.*)(?:\(|\(.*?\))(?:\))?(?:\:)?"
)  # simplify this abomination
RETURN = re.compile(r"\s*(?:return|) \(|(<.*>)|\)", flags=re.S)
INSERTION = re.compile(r"\{(\s+|\n|\t|)+<(.*)\}", flags=re.S)
INS_MODIFICATION = re.compile(r"(\s+)({(\s+)?<.*>(\s+)?})")
HTML_IMPORT = re.compile(r"from (.*) import html (.*)")
BROKEN_TEMPLATE = re.compile(r"dedent\(f\"\"\".*(<\/.*>\))")
HTML_ELEMENT = re.compile(r"<.*>\n*.*\n*.*<\/.*>")
COMPONENTS = None


def component_regex(functions: list[str]):
    return re.compile(
        rf"<(?:{'|'.join(functions)}).*>\n*.*\n*.*<\/(?:{'|'.join(functions)})>"
    )
