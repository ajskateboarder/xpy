from pathlib import Path

from tempfile import TemporaryDirectory
import pytest
import sys
from runpy import run_path, run_module

import ast
from xpy.parser import parse


TEST_CODE = [
    """html colored_pg(__text, color, classes=None):
    if not classes:
        classes = [(<div></div>)]
    return "".join([
        <p style="color: {color}" class="{' '.join(classes)}">
            {__text}
        </p>
        for _ in range(3)
    ])""",
    """from random import choice
html main(__text):
    color = choice(['red', 'blue'])
    return (
        <colored_pg color={color}>
            main says {__text}
        </colored_pg>
    )
""",
]


def component(color, classes, html, ext=""):
    return f'<p style="color: {color}" class="{classes}">\n    {html}\n{ext}</p>'


@pytest.fixture
def tempdir():
    with TemporaryDirectory() as dirname:
        yield Path(dirname)


def test_file_parse(tempdir: Path):
    """Expect individual xpy to parse"""
    with tempdir:
        main_script = tempdir / "main.xpy"
        main_script.write_text("\n".join(TEST_CODE))
        with main_script.open("r", encoding="utf-8") as fh:
            assert ast.parse(parse(fh))


def test_module_parse(tempdir: Path):
    """Expect xpy that imports xpy to parse"""
    with tempdir:
        (tempdir / "cpg.xpy").write_text(TEST_CODE[0])
        main_script = tempdir / "main.xpy"
        main_script.write_text(f"from .cpg import html colored_pg\n{TEST_CODE[1]}")
        with main_script.open(encoding="utf-8") as fh:
            assert ast.parse(parse(fh))


@pytest.mark.depends(on=["test_file_parse"])
def test_file_valid_html(tempdir: Path):
    """Expect individual xpy to produce expected HTML"""
    with tempdir:
        main_script = tempdir / "main.xpy"
        output = tempdir / "output.py"
        main_script.write_text("\n".join(TEST_CODE))
        with main_script.open(encoding="utf-8") as fh:
            output.write_text(parse(fh))
        namespace = run_path(output)
        arg = (
            "<div></div>",
            "        main says Hello world",
            "        ",
        )
        assert namespace["main"]("Hello world") in (
            component("blue", *arg) * 3,
            component("red", *arg) * 3,
        )
        assert namespace["colored_pg"]("Hello world", "blue")


class add_path:
    def __init__(self, path):
        self.path = path

    def __enter__(self):
        sys.path.insert(0, self.path)

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            sys.path.remove(self.path)
        except ValueError:
            pass


@pytest.mark.depends(on=["test_module_parse"])
def test_module_valid_html(tempdir: Path):
    """Expect xpy that imports xpy to produce expected HTML"""
    with tempdir:
        cpg = tempdir / "cpg.xpy"
        cpg_output = tempdir / "cpg.py"
        main_script = tempdir / "main.xpy"
        output = tempdir / "output.py"

        cpg.write_text(TEST_CODE[0])
        main_script.write_text(f"from cpg import html colored_pg\n{TEST_CODE[1]}")
        with cpg.open(encoding="utf-8") as fh:
            cpg_output.write_text(parse(fh))
        with main_script.open(encoding="utf-8") as fh:
            output.write_text(parse(fh))

        with add_path(str(tempdir)):
            namespace = run_module("output")

        arg = (
            "<div></div>",
            "        main says Hello world",
            "        ",
        )
        assert namespace["main"]("Hello world") in (
            component("blue", *arg) * 3,
            component("red", *arg) * 3,
        )
        assert namespace["colored_pg"]("Hello world", "blue")
