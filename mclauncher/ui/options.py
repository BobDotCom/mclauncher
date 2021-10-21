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

import logging


__all__ = ("all_options", "all_groups", "max_verbosity")


class Option:
    def __init__(self, name=None, options=tuple(), flags=tuple(), **kwargs):
        self.name = name
        self.options = options
        self.flags = flags
        self.kwargs = kwargs

    @property
    def py_name(self):
        """self.name but formatted for a python variable"""
        return self.name.replace(" ", "_")


class Group:
    def __init__(self):
        self.options = []

    def add_option(self, option: Option):
        return self.options.append(option)


all_options = []
all_groups = []

all_options.append(Option(name="version", nargs="?", default=False,
                          help="Minecraft version. Release versions and snapshots all work. "
                               "Defaults to newest release."))

group = Group()
group.add_option(Option(name="client", options=("-c",), flags=("--client",), default=False, metavar="name",
                        help="Use a custom client, such as OptiFine or Impact. Client name is NOT case sensitive. "
                        "(Warning: The client needs to be installed, the launcher won't automatically install it.)"))
group.add_option(Option(name="fabric", flags=("--fabric",), nargs="?", default=False, const=True,
                        metavar="version", help="Use the fabric mod loader. Loader version is optional, defaults to "
                                                "newest release."))
group.add_option(Option(name="forge", flags=("--forge",), nargs="?", default=False, const=True,
                        metavar="version", help="Use the forge mod loader. Loader version is optional, defaults to "
                                                "newest release."))
all_groups.append(group)

all_options.append(Option(name="y", options=("-y",), default=False, action="store_true",
                          help="Bypass all prompts, automatically selecting yes for them."))
all_options.append(Option(name="no install", flags=("--no-install",), default=False, action="store_true",
                          help="Don't run the install script at all, "
                               "try to run locally installed version if possible."))

# noinspection PyProtectedMember
max_verbosity = int(max(logging._levelToName.keys()) / 10)

all_options.append(Option(name="manual auth", options=("-m",), flags=("--manual-auth",), action="store_true",
                          default=False,
                          help="Manually visit and paste url for authentication. When false, the script will create a "
                               "flask server on localhost, and automatically get the token after authenticating. "
                               "Defaults to false."))
