from __future__ import annotations

import re
import sys

from itertools import takewhile
from io import TextIOBase

from bs4 import BeautifulSoup

IS_HTML_DIRECTIVE = re.compile(r"(html|def) (.*)(\(|\((.*?)\))(?:\))?(?:\:)?")
RETURN = re.compile(r"\s*return (\(|<)(.*)(>|\)?)", flags=re.S)
INSERTION = re.compile(r"\{(\s+|\n|\t|)+<(.*)\}", flags=re.S)
INS_MODIFICATION = re.compile(r"(\s+)({(\s+)?<.*>(\s+)?})")
COMPONENTS = None


class SkipOver(Exception):
    pass


class Continue(Exception):
    pass


def preceding_indents(line: str):
    return len([n for n in takewhile(lambda x: x == "", line.split(" "))])


def parse_elements(soups: list[BeautifulSoup]) -> list[str]:
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
        return string


def element_to_function(elem: dict) -> str:
    args = ", ".join([f"{k}={wrap_f_string(v)}" for k, v in elem["attrs"].items()])
    function_call = f"{elem['name']}(f'{elem['innerHTML']}'{',' if args else ''}{args})"
    print(function_call, file=sys.stderr)
    return function_call


def parse(io: TextIOBase) -> str:
    code = list(map(lambda x: x.rstrip(), io.readlines())) + [""]

    line_index = 0
    html_func = None
    at_return = False
    function_name = None

    return_stmts: dict[str, list] = {}

    modified_code = ["from textwrap import dedent"]

    while line_index < len(code):
        line = code[line_index]

        try:
            # function opening
            if html := IS_HTML_DIRECTIVE.match(line):
                if html.group(1) == "def":
                    raise SkipOver()
                function_name = (
                    html.group().split(" ")[1].replace("(", "").replace("):", "")
                )
                modified_code.append(line.replace("html", "def", 1))
                html_func = function_name
                return_stmts[function_name] = []
                raise Continue()

        except SkipOver:
            pass

        except Continue:
            line_index += 1
            continue

        # return opening
        if function_name is not None and (ret := RETURN.match(line)):
            opening, content, _ = ret.groups()
            if opening == "(" and content == "":
                at_return = True
                modified_code.append(line)
                return_stmts[function_name].append(line)
                line_index += 1
                continue

        # function closing
        if html_func != None:
            if preceding_indents(line) == 0 or line.strip() == "":
                html_func = None
                modified_code.append(line)
                line_index += 1
                continue

        # return closing
        if at_return and html_func != None:
            return_stmts[function_name].append(line)
            if line.strip() == ")":
                at_return = False
                modified_code.append(line)
                line_index += 1
                continue

        # default case
        modified_code.append(line)
        line_index += 1

    modified_code = "\n".join(modified_code)

    for value in return_stmts.values():
        base_statement = "\n".join(value)
        final_indent = base_statement.split("\n")[-1][:-1]
        templated = base_statement.replace("return (", 'return dedent(f"""').replace(
            final_indent + ")", final_indent + '""").strip()'
        )
        modified_code = modified_code.replace(base_statement, templated)

    function_names = list(return_stmts.keys())
    COMPONENTS = re.compile(
        fr"<(?:{'|'.join(function_names)}).*>\n*.*\n*.*<\/(?:{'|'.join(function_names)})>"
    )

    selected_insertions = COMPONENTS.findall(modified_code)
    print(selected_insertions, fr"<(?:{'|'.join(function_names)}).*>\n*.*\n*<\/(?:{'|'.join(function_names)})>")
    function_calls = [
        element_to_function(function)
        for function in parse_elements(
            [BeautifulSoup(x, "html.parser") for x in selected_insertions]
        )
    ]

    for elem, function in zip(selected_insertions, function_calls):
        modified_code = modified_code.replace(elem.rstrip(), f"{{{function}}}")

    print(modified_code)
    return modified_code
