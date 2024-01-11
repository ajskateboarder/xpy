import xpy

from module import color_text
import module.color_text

import local

print(color_text.main("Hello world"))
print(module.color_text.main("Hello world"))
print(local.main("Hello world"))