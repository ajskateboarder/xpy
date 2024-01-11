"""Some stuff used for iterating over code"""

from __future__ import annotations
from dataclasses import dataclass


class SkipOver(Exception):
    pass


class Continue(Exception):
    pass


@dataclass
class Code:
    line_index: int = 0
    html_func: str | None = None
    at_return: bool = False
