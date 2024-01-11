# xpy

A no-nonsense HTML syntax preprocessor for Python, powered by magical Regex and the mystical import system.

```py
# project/doc.xpy #
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
# project/main.py #
import xpy

from doc import main

print(main("random color ahhhh!!!!"))
```