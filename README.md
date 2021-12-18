I am an upgraded version of [termcolor](https://pypi.org/project/termcolor/) that allows you to store colors as objects
and use addition/calling to apply them to text. Color objects can also validate whether you use the correct color
identifiers upon creation, so all errors can be caught early.

# Example
```python
import sys
from colorie import Color, colored, cprint

text = colored('Hello, World!', 'red', attrs=['reverse', 'blink'])
print(text)
cprint('Hello, World!', 'green', 'on_red')

RED_ON_CYAN = Color('red', 'on_cyan')
print(RED_ON_CYAN + 'Hello, World!')
print(RED_ON_CYAN('Hello, Universe!'))

for i in range(10):
    cprint(i, 'magenta', end=' ')

cprint("Attention!", 'red', attrs=['bold'], file=sys.stderr)

RED = Color('red')
ON_WHITE = Color(highlight='on_white')
RED_ON_WHITE = RED + ON_WHITE
print(RED + "I am red" + " and I am red!")
print(RED + "I am red on white!" + ON_WHITE)
```
# Installation
`pip install colorie`
# Text Properties

* Text colors
    * grey
    * red
    * green
    * yellow
    * blue
    * magenta
    * cyan
    * white

* Text highlights
    * on\_grey
    * on\_red
    * on\_green
    * on\_yellow
    * on\_blue
    * on\_magenta
    * on\_cyan
    * on\_white

* Attributes
    * bold
    * dark
    * underline
    * blink
    * reverse
    * concealed

# Terminal properties

> 
> 
> | Terminal     | bold    | dark | underline | blink      | reverse | concealed |
> | ------------ | ------- | ---- | --------- | ---------- | ------- | --------- |
> | xterm        | yes     | no   | yes       | bold       | yes     | yes       |
> | linux        | yes     | yes  | bold      | yes        | yes     | no        |
> | rxvt         | yes     | no   | yes       | bold/black | yes     | no        |
> | dtterm       | yes     | yes  | yes       | reverse    | yes     | yes       |
> | teraterm     | reverse | no   | yes       | rev/red    | yes     | no        |
> | aixterm      | normal  | no   | yes       | no         | yes     | yes       |
> | PuTTY        | color   | no   | yes       | no         | yes     | no        |
> | Windows      | no      | no   | no        | no         | yes     | no        |
> | Cygwin SSH   | yes     | no   | color     | color      | color   | yes       |
> | Mac Terminal | yes     | no   | yes       | yes        | yes     | yes       |
>
