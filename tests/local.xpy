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