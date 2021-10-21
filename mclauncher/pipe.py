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
import re
import threading
import os

logging.basicConfig(level=0,
                    format="%(asctime)s [%(levelname)s] (%(name)s): %(message)s")


class LogPipe(threading.Thread):
    """
    Credits to https://stackoverflow.com/a/61111999 for the original implementation of this.
    """

    def __init__(self, logger: logging.Logger) -> None:
        """
        Initialize the object as a mock PIPE that logs to :param:`logger` in :meth:`.write`. For use with
        :class:`subprocess.Popen`. 

        Parameters
        -----------
        logger: :class:`logging.Logger`
            The logger to use in this object.
        """
        super().__init__()
        self.daemon = False
        self.fdRead, self.fdWrite = os.pipe()
        self.pipeReader = os.fdopen(self.fdRead)
        self.start()
        self.logger = logger
        self.regex = re.compile(r"^\[(?:\d{2}:){2}\d{2}] \[(?P<name>.+)/(?P<level>[A-Z]+)]: (?P<message>.+)", re.DOTALL)

    def fileno(self):
        """Return the write file descriptor of the pipe"""
        return self.fdWrite

    def run(self):
        """Run the thread, logging everything."""
        for line in iter(self.pipeReader.readline, ''):
            match = re.search(self.regex, line.strip("\n"))
            if match:
                name, level, message = match.groups()
            else:
                name, level, message = "Java", "INFO", line

            message = f"{name} - {message}"

            level = logging.getLevelName(level)
            self.logger.log(level, message)

        self.pipeReader.close()

    def close(self):
        """Close the write end of the pipe."""
        os.close(self.fdWrite)
