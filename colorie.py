# Copyright (c) 2008-2011 Volvox Development Team
# Copyright (c) 2021 Stanislav Zmiev
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# Authors: Konstantin Lepa <konstantin.lepa@gmail.com>,
#          Stanislav Zmiev <szmiev2000@gmail.com>

"""ANSII Color formatting for output in terminal"""

import os
from typing import Iterable, Optional, Sequence, Union, overload

__ALL__ = ["Color", "colored", "cprint"]

ANSII_ESCAPE = "\33[{codes}m"
RESET = ANSII_ESCAPE.format(codes="0")

ATTRIBUTES = dict(zip(["bold", "dark", "", "underline", "blink", "", "reverse", "concealed"], range(1, 9)))
COLORS = dict(zip(["grey", "red", "green", "yellow", "blue", "magenta", "cyan", "white"], range(30, 38)))
HIGHLIGHTS = dict(zip([f"on_{color}" for color in COLORS], range(40, 48)))
del ATTRIBUTES[""]


class Color:
    """Encapsulate a color as an object for repeated use

    The __init__ arguments are the same as in colorize(...).

    Colors can be combined or used to color strings.
    Note: the sum of Color and str returns a ColoredString object.
    If you wish to use it in operations besides addition or print,
    you should convert it back to str.

    Usage:
    >>> BLINKING_BLUE_ON_YELLOW = Color("blue", "on_yellow", ["blink"])
    >>> RED = Color("red")
    >>> red_text = RED + "I and only I will be red"
    >>> other_red_text = RED("I will also be red")
    >>> ON_WHITE = Color(highlight="on_white")
    >>> red_on_white_text = red_text + ON_WHITE
    >>> RED_ON_WHITE = RED + ON_WHITE
    """

    __slots__ = "color", "highlight", "attrs"
    color: Optional[str]
    highlight: Optional[str]
    attrs: Sequence[str]

    def __init__(self, color: str = None, highlight: str = None, attrs: Sequence[str] = (), strict=True) -> None:
        if strict:
            validate_args(color, highlight, attrs)
        self.color = color
        self.highlight = highlight
        self.attrs = attrs

    def __str__(self) -> str:
        return colored("", self.color, self.highlight, self.attrs, strict=False, reset=False)

    def __repr__(self) -> str:
        return str(self + f"Color(color={self.color}, highlight={self.highlight}, attrs={self.attrs})")

    def __call__(self, other):
        return self + other

    @overload
    def __add__(self, other: "Color") -> "Color":
        ...

    @overload
    def __add__(self, other: str) -> "ColoredString":
        ...

    @overload
    def __add__(self, other: "ColoredString") -> "ColoredString":
        ...

    def __add__(self, other):
        if isinstance(other, Color):
            return Color(
                self.color or other.color,
                self.highlight or other.highlight,
                tuple(set(*self.attrs, *other.attrs)),
                False,
            )
        elif isinstance(other, str):
            return ColoredString(other, self, False)
        elif isinstance(other, ColoredString):
            return ColoredString(other.original_str, self + other.color, False)

    def __radd__(self, other: str) -> "ColoredString":
        return self + other

    def __eq__(self, other: "Color") -> bool:
        return self.color == other.color and self.highlight == other.highlight and self.attrs == other.attrs


class ColoredString:
    __slots__ = "original_str", "color"
    original_str: str
    color: Color

    def __init__(self, original_str: str, color: Color, strict=True):
        if strict:
            validate_args(color.color, color.highlight, color.attrs)
        self.original_str = original_str
        self.color = color

    def __str__(self) -> str:
        return colored(self.original_str, self.color.color, self.color.highlight, self.color.attrs, strict=False)

    def __repr__(self) -> str:
        return f"ColoredString(original_str={self.original_str}, color={repr(self.color)})"

    def __add__(self, other: Union[Color, str, "ColoredString"]) -> "ColoredString":
        if isinstance(other, Color):
            return other + self
        elif isinstance(other, str):
            return ColoredString(self.original_str + other, self.color, False)
        elif isinstance(other, ColoredString):
            return ColoredString(self.original_str + other.original_str, self.color + other.color, False)
        else:
            raise NotImplementedError(f'Cannot add "ColoredString" to "{type(other)}"')

    def __radd__(self, other: str) -> "ColoredString":
        return ColoredString(other + self.original_str, self.color, False)


def colored(
    text: str,
    color: str = None,
    highlight: str = None,
    attrs: Iterable[str] = (),
    strict=False,
    reset=True,
) -> str:
    """Colorize text

    Available text colors:
        red, green, yellow, blue, magenta, cyan, white.

    Available text highlights:
        on_red, on_green, on_yellow, on_blue, on_magenta, on_cyan, on_white.

    Available attributes:
        bold, dark, underline, blink, reverse, concealed.

    Example:
        colored('Hello, World!', 'red', 'on_grey', ['bold', 'blink'])
        colored('Hello, World!', 'green')
    """
    color = color.lower() if color is not None else None
    highlight = highlight.lower() if highlight is not None else None
    attrs = [a.lower() for a in attrs]
    if strict:
        validate_args(color, highlight, attrs)
    if os.getenv("ANSI_COLORS_DISABLED") is None:
        sequence = (COLORS.get(color), HIGHLIGHTS.get(highlight), *(ATTRIBUTES.get(a) for a in attrs))
        formatted_sequence = ";".join([str(code) for code in sequence if code])
        text = f"{ANSII_ESCAPE.format(codes=formatted_sequence)}{text}" + (RESET if reset else "")
    return text


def cprint(text, color: str = None, highlight: str = None, attrs: Iterable[str] = (), strict=False, **kwargs) -> None:
    """Print colorized text.

    It accepts arguments of print function.
    """
    print(colored(text, color, highlight, attrs, strict), **kwargs)


def validate_args(color: Optional[str], highlight: Optional[str], attrs: Iterable[str]) -> None:
    to_validate = [("attrs", a, ATTRIBUTES) for a in attrs]

    if highlight is not None:
        to_validate.append(("highlight", highlight, HIGHLIGHTS))
    if color is not None:
        to_validate.append(("color", color, COLORS))
    for arg_name, arg, dict_with_escape_codes in to_validate:
        if arg.lower() not in dict_with_escape_codes:
            raise KeyError(f'Invalid {arg_name} argument: "{arg}"')


if __name__ == "__main__":
    LINE = "-" * 78
    print(f"Current terminal type: {os.getenv('TERM')}")
    print("Test basic colors:")
    cprint("Grey color", "grey")
    cprint("Red color", "red")
    cprint("Green color", "green")
    cprint("Yellow color", "yellow")
    cprint("Blue color", "blue")
    cprint("Magenta color", "magenta")
    cprint("Cyan color", "cyan")
    cprint("White color", "white")
    print(LINE)

    print("Test highlights:")
    cprint("On grey color", highlight="on_grey")
    cprint("On red color", highlight="on_red")
    cprint("On green color", highlight="on_green")
    cprint("On yellow color", highlight="on_yellow")
    cprint("On blue color", highlight="on_blue")
    cprint("On magenta color", highlight="on_magenta")
    cprint("On cyan color", highlight="on_cyan")
    cprint("On white color", color="grey", highlight="on_white")
    print(LINE)

    print("Test attributes:")
    cprint("Bold grey color", "grey", attrs=["bold"])
    cprint("Dark red color", "red", attrs=["dark"])
    cprint("Underline green color", "green", attrs=["underline"])
    cprint("Blink yellow color", "yellow", attrs=["blink"])
    cprint("Reversed blue color", "blue", attrs=["reverse"])
    cprint("Concealed Magenta color", "magenta", attrs=["concealed"])
    cprint("Bold underline reverse cyan color", "cyan", attrs=["bold", "underline", "reverse"])
    cprint("Dark blink concealed white color", "white", attrs=["dark", "blink", "concealed"])
    print(LINE)

    print("Test mixing:")
    cprint("Underline red on grey color", "red", "on_grey", ["underline"])
    cprint("Reversed green on red color", "green", "on_red", ["reverse"])
    print(LINE)

    print("Test Color objects:")
    print(Color("red") + "Red on" + " white color" + Color(highlight="on_white"))
    print("Underline red on grey color" + Color("red", "on_grey", ["underline"]))
