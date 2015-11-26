# Text Colors
# Issue:
# Colored lines that contain newlines do not display correctly in less, they
# lose their color on the far side of the newline. I could fix this by
# looking for newlines and re-establishing the color afterwards.
'''
Use to access strings that control the colors produced by a terminal. The
possible colors are:
    black, red, green, yellow, blue, magenta, cyan, and white
    Black, Red, Green, Yellow, Blue, Magenta, Cyan, and White
Capitalized versions are bolder than lower case versions.

Once you instantiate the Colors class, then you can color a string using
something like:
    colors = textcolors.Colors()
    print colors('blue', 'Hello world!")

It is also possible to put color directives in the text string itself. In this
case you would only provide one string, the text, but it would contain color
directives embedded in angle brackets. For example:
    print colors('<red>Error:<none> Expected a number.')

Alternatively, you can access the color strings themselves by treating the
object as a dictionary where the colors are the keys. In addition, 'none' is
the key for the string that returns the color back to normal.
Ex.
    print colors['blue'] + 'Hello world!' + colors['none']

Or, you can access the color strings by using the desired color as an attribute
of the Colors object.
Ex.
    print colors.blue + 'Hello world!' + colors.none

You can create color aliases using addAlias()
    colors.addAlias('hot', 'red')
    colors.addAlias('cold', 'cyan')
    print colors('hot', '100C')
    print colors('cold', '0C')

You can disable or re-enable the colors by calling colors.colorize().

The colorizer method returns a function that when called with a string argument
returns that string in the color given with the colorizer method was created.
    status = colors.colorizer('blue')
    fails = colors.colorizer('red')
    print status('Running test ...')
    ...
    if failure: print fails('FAIL')
'''

from __future__ import division, print_function
import re
import os, sys
_colorRegex = re.compile('<[a-zA-Z_]+>')
_colorCodeRegex = re.compile('\033' + r'\[[01](;\d\d)?m')

# colors should be all lower case (order of colors is significant)
# color names are expected to be simple identifiers that contain upper and
# lower letters and underscores only.
_BaseColors = ['black','red','green','yellow','blue','magenta','cyan','white']

def stripColors(text):
    """
    Strip the color codes from a string.
    """
    return _colorCodeRegex.sub('', text)

def isTTY(stream=sys.stdout):
    """
    Is stream connected to a TTY.

    One generally does not want to colorize a stream such as stdout or
    stderr if it being redirected to a file. This function returns True if
    passed a stream that is connected to a TTY. Can be used to turn off
    colors for streams that do not go to a TTY.
    """
    return os.isatty(stream.fileno())

class Colors:
    def __init__(self, wantColors = True):
        self.aliases = {}
        self.colors = {}
        self.colorize(wantColors)
        self.cycleIndex = 0

    def __getitem__(self, color):
        return self.colors[color]

    def __getattr__(self, color):
        return self.colors[color]

    def generator(self, skip=None):
        """Returns a generator that cycles through available colors.

        Usage:
            colorGenerator = colors.gen(['black', 'white'])
            color = colorGenerator.next()
        """
        if skip == None:
            skip = []
        while True:
            for color in _BaseColors:
                if color in skip:
                    continue
                yield color

    def __call__(self, *args):
        """
        Colorize a text string.

        If given with one argument, that argument is taken to be a text string
        that contains embedded color commands. Here is an example:
            print color('<red>Error:<none> expected a real number.')
        The color is returned to none at the end of the text, so it is not
        necessary to do it explicitly.

        Otherwise there is expected to be two arguments, both strings. The
        first is the name of the color, the second would be the text string. In
        this case, the whole string will be converted to that color. Example:
            print color('red', 'Error:'), 'expected a real number.'
        """
        if len(args) == 1:
            # perform color replacments on the text string
            def replaceColor(found):
                try:
                    return self.colors[found.group(0)[1:-1]]
                except KeyError:
                    return found.group(0)
            return _colorRegex.sub(replaceColor, args[0]) + self.colors['none']
        elif len(args) == 2:
            return self.colors[args[0]] + args[1] + self.colors['none']
        else:
            raise AssertionError

    def colorize(self, wantColors):
        """
        Turn on or turn off the color generation feature.
        """
        self.wantColors = wantColors
        if wantColors:
            for index, color in enumerate(_BaseColors):
                self.colors[_capitalize(color)] = '\033[1;3%dm' % index
                self.colors[color] = '\033[0;3%dm' % index
            self.colors['none'] = '\033[0m'
            for alias, color in self.aliases.items():
                self.colors[alias] = self.colors[color]
        else:
            for color in _BaseColors:
                self.colors[_capitalize(color)] = ''
                self.colors[color] = ''
            self.colors['none'] = ''
            for alias in self.aliases:
                self.colors[alias] = ''

    def addAlias(self, new, existing):
        """Add new name that can be used to refer to a color."""
        self.aliases[new] = existing
        if self.wantColors:
            self.colors[new] = self.colors[existing]
        else:
            self.colors[new] = ''

    def colorizer(self, color):
        """
        Return a colorizer.

        Returns an function that if called with one string argument returns that
        argument colored using the color specified with the function was created.
        """
        return lambda text: self(color, text)

    def printer(self, color):
        """
        Color printer

        Returns a function that when called prints a string to stdout in the 
        specified color.
        """
        return lambda text: print(self(color, text))


def _capitalize(arg):
    return arg[0].upper() + arg[1:]

if __name__ == "__main__":
    colors =  Colors()
    for color in _BaseColors:
        Color = color.title()
        offset = (16 - 2*len(color))* ' '
        print("%s:" % color, offset, colors(color, color), colors(Color, Color))
