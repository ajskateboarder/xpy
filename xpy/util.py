"""String utilities"""

from __future__ import annotations
from typing import TypedDict
from bs4 import BeautifulSoup


class ParsedElement(TypedDict):
    name: str
    attrs: dict[str, str]
    innerHTML: str


def parse_elements(elements: list[str]) -> list[ParsedElement]:
    soups = [BeautifulSoup(x, "html.parser") for x in elements]

    for soup in soups[:]:
        if len(soup.contents) == 2:
            start = soup.contents[0]
            if start.startswith(">") and not start.endswith(">"):
                soups[soups.index(soup)] = BeautifulSoup(
                    "".join(list(reversed(soup.contents))), "html.parser"
                )

    return [
        {
            "name": element.name,
            "attrs": element.attrs,
            "innerHTML": element.text.strip(),
        }
        for soup in soups
        if (element := list(soup.children)[0])
    ]


def wrap_f_string(string: str) -> str:
    if string.startswith("{") and string.endswith("}"):
        return 'f"' + string + '"'
    else:
        return f'"{string}"'


def element_to_function(elem: dict) -> str:
    attrs: dict = elem["attrs"]
    args = ", ".join([f"{k}={wrap_f_string(v)}" for k, v in attrs.items()])
    quote = "'" if '"' in elem["innerHTML"] else '"'
    if quote == "'":
        function_call = f"{elem['name']}(f{quote}{elem['innerHTML']}{quote}{',' if args else ''}{args})"
    else:
        function_call = f'{elem["name"]}(f{quote}{elem["innerHTML"]}{quote}{"," if args else ""}{args})'
    return function_call
