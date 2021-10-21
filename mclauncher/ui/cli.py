"""
MIT License

Copyright (c) 2021-present BobDotCom

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

"""
import argparse
from .options import all_options, all_groups, max_verbosity
from .. import __version__



__all__ = ('parser', 'max_verbosity')


parser = argparse.ArgumentParser()

for o in all_options:
    parser.add_argument(*o.flags, *o.options, dest=o.py_name, **o.kwargs)

parser.add_argument('--version', "-V", action='version', version='%(prog)s ' + __version__)
all_options.append(Option(name="verbose", options=("-v",), flags=("--verbose",), action="count", default=0,
                          help=f"Set verbosity. Can be supplied multiple times to increase verbosity, "
                               f"max {max_verbosity}."))

for g in all_groups:
    group = parser.add_mutually_exclusive_group()
    for o in g.options:
        group.add_argument(*o.flags, *o.options, dest=o.py_name, **o.kwargs)

all_options.append(Option(name="version", options=("-V",), flags=("--version",), action="version",
                          version="%(prog)s 0.0.1",
                          help="show program's version number and exit"))
"""
