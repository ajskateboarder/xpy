import xpy

from pathlib import Path
from os.path import basename
from types import FunctionType, ModuleType
import pytest


@pytest.fixture(autouse=True)
def change_test_dir(monkeypatch):
    if basename(Path.cwd()) != "tests":
        monkeypatch.chdir("tests")


def colors(insert):
    return (
        f'<p style="color: blue">\n    {insert}\n</p>',
        f'<p style="color: red">\n    {insert}\n</p>',
    )


def test_module_import():
    import module.color_text as _color_text
    from module import color_text
    from module import colored_pg

    import module

    assert isinstance(module, ModuleType)
    assert isinstance(color_text, ModuleType)
    assert isinstance(_color_text, ModuleType)
    assert isinstance(_color_text.main, FunctionType)
    assert isinstance(color_text.colored_pg, FunctionType)
    assert isinstance(colored_pg, FunctionType)

    components = colors("<span>Individual component!!</span> Hello world 1")
    assert module.color_text.main("Hello world") in components
    assert color_text.main("Hello world") in components
    assert _color_text.main("Hello world") in components
    assert _color_text.colored_pg("Hello world 1", "red") == components[1]


def test_local_import():
    import local
    from local import main
    from local import colored_pg

    assert isinstance(local, ModuleType)
    assert isinstance(main, FunctionType)
    assert isinstance(colored_pg, FunctionType)

    assert local.main("Hello world") in colors("Hello world 1")
    assert local.colored_pg("Hello world", "red") == colors("Hello world")[1]
