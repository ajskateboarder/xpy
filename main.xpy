from random import (
    choice
)

html list_item(
    __text: str,
    key: int = 1):
    return (
        <li key={key - 1}>{__text}
        </li>
    )

html main():
    if choice([True, False]):
        print("hello random world")
    else:
        print("hiii")
    return (
        <ul>
            {<list_item key={1}>Hello world</list_item>}
            {<list_item key={1}></list_item>}
        </ul>
    )
