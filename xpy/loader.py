import sys
import types

import importlib.abc
import importlib.machinery
from pathlib import Path

from .parser import parse


class XPYFinder(importlib.abc.MetaPathFinder):
    def __init__(self, path):
        self.path = path

    def find_spec(self, module, path, target=None):
        path = (Path(path or ".") / f"{module}.xpy").absolute()
        with open(path) as fh:
            source = parse(fh)

        loader = XPYLoader(module, source, path)
        return importlib.machinery.ModuleSpec(module, loader, origin=path)


class XPYLoader(importlib.abc.Loader):
    def __init__(self, module_name, source, path) -> None:
        self.module_name = module_name
        self.source = source
        self.path = path

    def create_module(self, spec):
        module = sys.modules.get(spec.name)
        if module is None:
            module = types.ModuleType(spec.name)
            sys.modules[spec.name] = module
        return module

    def exec_module(self, module):
        module.__file__ = self.path
        exec(self.source, module.__dict__)
        return module

    def get_source(self, name):
        return self.source


def add_all_xpys():
    for xpy_path in Path.cwd().glob("**/*.xpy"):
        sys.meta_path.append(XPYFinder(xpy_path))
