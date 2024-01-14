"""XPy code parser"""

from __future__ import annotations

from io import TextIOBase

from . import util, regx


def parse(io: TextIOBase) -> str:
    """Parse XPy code as plain Python"""

    code = list(map(lambda x: x.rstrip(), io.readlines())) + [""]
    modified_code = "\n".join(["from textwrap import dedent"] + code)
    function_names = [e[1] for e in regx.HTML_IMPORT.findall(modified_code)]

    for function_sig in regx.HTML_DIRECTIVE.findall(modified_code):
        function_sig = list(function_sig)
        function_names.append(function_sig[1])
        modified_code = modified_code.replace(
            " ".join(function_sig), " ".join(["def"] + function_sig[1:])
        )

    # replace all html element references with escaped
    for component in regx.HTML_ELEMENT.findall(modified_code):
        escaped_component = f'f"""{component}"""'
        modified_code = modified_code.replace(component, escaped_component, 1)

    # replace html imps. with regular ones
    lines = regx.HTML_IMPORT.findall(modified_code)

    for _, func in lines:
        function_names.append(func)

    original_lines = [f"from {mod} import html {func}" for mod, func in lines]
    regular_lines = [f"from {mod} import {func}" for mod, func in lines]

    # convert all user-defd components into function calls
    for og_line, reg_line in zip(original_lines, regular_lines):
        modified_code = modified_code.replace(og_line, reg_line)
    regx.COMPONENTS = regx.component_regex(function_names)

    selected_insertions = regx.COMPONENTS.findall(modified_code)
    function_calls = [
        util.element_to_function(function)
        for function in util.parse_elements(selected_insertions)
    ]

    for elem, function in zip(selected_insertions, function_calls):
        modified_code = modified_code.replace(elem.rstrip(), f"{{{function}}}")

    return modified_code
