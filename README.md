# XPy

A no-nonsense HTML syntax preprocessor for Python, powered by magical Regex, BeautifulSoup4, and the mystical import system. XPy converts JSX-esque code written in ".xpy" files into plain Python code with f-strings at import-time, with no build step required.

```py
# doc.xpy
from random import choice

html colored_pg(__text, color):
    return (
        <p style="color: {color}">
            {__text}
        </p>
    )

html main(__text):
    color = choice(['red', 'blue'])
    return (
        <colored_pg color={color}>
            {__text} 1
        </colored_pg>
    )
```

```py
# main.py
import xpy.load

from doc import main

print(main("random color ahhhh!!!!"))
```

## Structuring

You should structure elements in modules as follows:

```text
module /
  __init__.py
  element.xpy
  element.pyi
```

`element.pyi` includes type stubs for `element.xpy` so your IDE doesn't freak out when you try to import an xpy module.

You can test XPy's import hook and code generation using pytest.

```bash
pip install pytest
pytest
```

## VSCode syntax highlighting

Install the XPy syntax highlight extension by copying the `xpy-language` to your extensions in the `.vscode` folder, or `.vscode-oss` for VSCodium, and then restart VSCode.

```bash
cp -r xpy-language ~/.vscode-oss/extensions
```

## Stuff to implement

- Fragment elements
- Basic syntax errors, similar to Rust's [typed_html](https://docs.rs/typed-html/) crate
- Build CSS styles from objects, similar to React styles
