from __future__ import annotations

import re

from itertools import takewhile
from io import TextIOBase

from bs4 import BeautifulSoup

IS_HTML_DIRECTIVE = re.compile(r"(html|def) (.*)(\(|\((.*?)\))(?:\))?(?:\:)?")
RETURN = re.compile(r"\s*return (\(|<)(.*)(>|\)?)", flags=re.S)
INSERTION = re.compile(r"\{(\s+|\n|\t|)+<(.*)\}", flags=re.S)
INS_MODIFICATION = re.compile(r"(\s+)({(\s+)?<.*>(\s+)?})")


class SkipOver(Exception):
    pass


class Continue(Exception):
    pass


def preceding_indents(line: str):
    return len([n for n in takewhile(lambda x: x == "", line.split(" "))])


def find_insertions(
    base_insertions: list[str], full_code: str
) -> list[str | list[str]]:
    selected_insertions = []

    for insertion in base_insertions:
        if insertion not in full_code:
            indent = insertion.split("}")[0].split("\n")[1]

            # i guess this can be slow but it works :)
            def try_insertion(insertion, n=0):
                final_insertion = insertion.replace("{", f"{indent}{{\n{(' ' * n)}")
                if final_insertion in full_code:
                    return final_insertion
                else:
                    return try_insertion(insertion, n + 1)

            if _insertion := try_insertion(insertion):
                insertion = _insertion

        if insertion != "}":
            selected_insertions.append(insertion)

    selected_insertions = [
        ins.replace("{", "").replace("}", "").strip() for ins in selected_insertions
    ]
    selected_insertions = [
        [ins] if ins.startswith("<") and ins.endswith(">") else ins
        for ins in selected_insertions
    ]

    return selected_insertions


def flatten(lis):
    rt = []
    for i in lis:
        if isinstance(i, list):
            rt.extend(flatten(i))
        else:
            rt.append(i)
    return rt


def join_insertions(insertions):
    new_insertions = []

    for i, insertion in enumerate(insertions):
        if isinstance(insertion, list):
            new_insertions.append(insertion)
        if isinstance(insertion, str) and (i + 1) != len(insertions):
            new_insertions.append(insertion + insertions[i + 1])

    return flatten(new_insertions)


def parse_elements(soups: list[BeautifulSoup]) -> list[str]:
    for soup in soups[:]:
        if len(soup.contents) == 2:
            start = soup.contents[0]
            if start.startswith(">") and not start.endswith(">"):
                soups[soups.index(soup)] = BeautifulSoup("".join(list(reversed(soup.contents))), "html.parser")
    print(soups)

    return [
        {
            "name": element.name,
            "attrs": element.attrs,
            "innerHTML": element.text.strip(),
        }
        for soup in soups
        if (element := list(soup.children)[0])
    ]


def element_to_function(elem: dict) -> str:
    args = ", ".join([f"{k}={v}" for k, v in elem["attrs"].items()])
    return f"{elem['name']}('{elem['innerHTML']}'{',' if args else ''}{args})"


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

    base_insertions = [
        i + "}"
        for i in (
            next(
                "{<" + item
                for item in INSERTION.findall(modified_code)[0]
                if item.strip() != ""
            )
            + "}"
        ).split("}")
    ]

    selected_insertions = join_insertions(
        find_insertions(base_insertions, modified_code)
    )

    function_calls = parse_elements(
        [BeautifulSoup(x, "html.parser") for x in selected_insertions]
    )
    elem_calls = ["".join(match) for match in INS_MODIFICATION.findall(modified_code)]
    elem_calls = [elem for elem in elem_calls if any(func in elem for func in return_stmts.keys())]
    
    for elem, function in zip(elem_calls, function_calls):
        modified_code = modified_code.replace(elem.rstrip(), f"{{{element_to_function(function)}}}")

    return modified_code
