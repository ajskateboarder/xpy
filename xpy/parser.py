from __future__ import annotations

from io import TextIOBase

from . import util, regx
from .state import Continue, SkipOver, Code


def parse(io: TextIOBase) -> str:
    code = list(map(lambda x: x.rstrip(), io.readlines())) + [""]
    return_stmts: dict[str, list] = {}

    modified_code = ["from textwrap import dedent"]
    c = Code()

    while c.line_index < len(code):
        line = code[c.line_index]

        try:
            # function opening
            if html := regx.IS_HTML_DIRECTIVE.match(line):
                if html.group(1) == "def":
                    raise SkipOver
                function_name = (
                    html.group().split(" ")[1].replace("(", "").replace("):", "")
                )
                modified_code.append(line.replace("html", "def", 1))
                c.html_func = function_name
                return_stmts[function_name] = []
                raise Continue

        except SkipOver:
            pass

        except Continue:
            c.line_index += 1
            continue

        # return opening
        if c.html_func is not None and (ret := regx.RETURN.match(line)):
            opening, content, _ = ret.groups()
            if opening == "(" and content == "":
                c.at_return = True
                modified_code.append(line)
                return_stmts[c.html_func].append(line)
                c.line_index += 1
                continue

        # function closing
        if c.html_func != None:
            if util.preceding_indents(line) == 0 or line.strip() == "":
                c.html_func = None
                modified_code.append(line)
                c.line_index += 1
                continue

        # return closing
        if c.at_return and c.html_func != None:
            return_stmts[function_name].append(line)
            if line.strip() == ")":
                c.at_return = False
                modified_code.append(line)
                c.line_index += 1
                continue

        # default case
        modified_code.append(line)
        c.line_index += 1

    modified_code = "\n".join(modified_code)

    for value in return_stmts.values():
        base_statement = "\n".join(value)
        final_indent = base_statement.split("\n")[-1][:-1]
        templated = base_statement.replace("return (", 'return dedent(f"""').replace(
            final_indent + ")", final_indent + '""").strip()'
        )
        modified_code = modified_code.replace(base_statement, templated)

    regx.COMPONENTS = regx.component_regex(list(return_stmts.keys()))

    selected_insertions = regx.COMPONENTS.findall(modified_code)
    function_calls = [
        util.element_to_function(function)
        for function in util.parse_elements(selected_insertions)
    ]

    for elem, function in zip(selected_insertions, function_calls):
        modified_code = modified_code.replace(elem.rstrip(), f"{{{function}}}")

    return modified_code
