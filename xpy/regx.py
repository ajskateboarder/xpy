"""Regular expressions"""

from __future__ import annotations
import re

IS_HTML_DIRECTIVE = re.compile(r"(html|def) (.*)(\(|\((.*?)\))(?:\))?(?:\:)?")
RETURN = re.compile(r"\s*return (\(|<)(.*)(>|\)?)", flags=re.S)
INSERTION = re.compile(r"\{(\s+|\n|\t|)+<(.*)\}", flags=re.S)
INS_MODIFICATION = re.compile(r"(\s+)({(\s+)?<.*>(\s+)?})")
COMPONENTS = None


def component_regex(functions: list[str]):
    return re.compile(
        rf"<(?:{'|'.join(functions)}).*>\n*.*\n*.*<\/(?:{'|'.join(functions)})>"
    )
