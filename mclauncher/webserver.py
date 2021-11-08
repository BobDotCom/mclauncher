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

import io
import multiprocessing
import time
from typing import Optional, Callable

import requests
import click

from flask import Flask, request, current_app
import logging


def override_logger(log_level):
    logging.basicConfig(level=log_level, format="%(asctime)s [%(levelname)s] (%(name)s): %(message)s")

    global logger
    logger = logging.getLogger(__name__)
    logging.getLogger('werkzeug').setLevel(log_level)
    loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
    for logger in loggers:
        logger.setLevel(log_level)

    click_echo = click.echo
    click_secho = click.secho

    def secho(message=None, file=None, nl=True, err=False, color=None, **styles):
        file = file or io.StringIO()
        click_secho(message, file, nl, err, color, **styles)
        logger.info(file.getvalue())
        file.close()

    def echo(message=None, file=None, nl=True, err=False, color=None):
        file = file or io.StringIO()
        click_echo(message, file, nl, err, color)
        logger.info(file.getvalue())
        file.close()

    click.echo = echo
    click.secho = secho


logger = logging.getLogger(__name__)
app = Flask(__name__)


@app.after_request
def response_processor(response):
    @response.call_on_close
    def process_after_request():
        with app.app_context():
            # noinspection PyUnresolvedReferences
            current_app.f.put(True)

    return response


response_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Authorized</title>
</head>
<body>
<h1>Authorized</h1>
<p id="description">You may close this window.</p>
<p>Minecraft should launch momentarily. (approx. 15 seconds)</p>
<script>
    const closeAfter = 30;
    document.getElementById("description").innerText += " It will automatically close after " + closeAfter + " seconds."
    setTimeout(() => window.close(), closeAfter * 1000)
</script>
</body>
</html>"""


@app.route("/")
def recieve_code():
    # noinspection PyUnresolvedReferences
    current_app.q.put(request.args['code'])
    return response_html


def start_server(port: int, q: multiprocessing.Queue, f: multiprocessing.Queue,
                 log_level: int) -> None:
    override_logger(log_level)
    with app.app_context():
        current_app.q = q
        current_app.f = f
    app.run(port=port)


def stop_server(p: multiprocessing.Process) -> None:
    p.terminate()


def run_server(when_ready: Optional[Callable[[], None]] = None, port: int = 5000, log_level: int = 30) -> str:
    override_logger(log_level)
    logger.info('Starting up webserver')
    q = multiprocessing.Queue()
    f = multiprocessing.Queue()
    p = multiprocessing.Process(target=start_server, args=(port, q, f, log_level))
    p.start()
    logger.info('Webserver started up')
    if when_ready is not None:
        logger.info('Executing when_ready')
        time.sleep(0.5)  # give the server a moment to start up
        good = False
        for _ in range(150):
            try:
                req = requests.get(f"http://localhost:{port}/")
            except requests.exceptions.ConnectionError:
                time.sleep(0.1)
            else:
                if req.status_code == 400:
                    good = True
                    break
        if not good:
            raise RuntimeError("failed to connect to localhost")
        when_ready()
    logger.info("Waiting for code")
    code = q.get(block=True)
    logger.info("Received code")
    logger.info("Shutting down webserver")
    f.get(block=True)
    stop_server(p)
    logger.info('Webserver shut down')
    return code
