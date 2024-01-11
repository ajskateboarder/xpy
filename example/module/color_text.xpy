from random import choice
from .cpg import colored_pg

html main(__text):
    color = choice(['red', 'blue'])
    return (
        <colored_pg color={color}>
            {__text} 1
        </colored_pg>
    )