# XPy

A no-nonsense HTML syntax preprocessor for Python, powered by magical Regex, BeautifulSoup4, and the mystical import system.

```py
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
import xpy

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

All styles of importing *should work*, either when you import an xpy file from Python (or vice-versa), or when you import an xpy file from xpy itself. Try out the example kitchen-sink!
