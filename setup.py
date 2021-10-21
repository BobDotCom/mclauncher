import codecs
import os.path
import re

import setuptools


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


# The full version, including alpha/beta/rc tags
with open('mclauncher/__init__.py') as f:
    __version__ = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1) or ''

with open("README.rst", "r") as fh:
    long_description = fh.read().replace("""===================
mclauncher
===================""", """===================
mclauncher {0}
===================""".format(__version__))

packages = [
    "mclauncher",
    "mclauncher.ui"
]

setuptools.setup(
    name="mclauncher",
    version=__version__,
    author="BobDotCom",
    author_email="bobdotcomgt@gmail.com",
    description="A minecraft launcher made in python.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/BobDotCom/mclauncher",
    download_url='https://github.com/BobDotCom/mclauncher/releases',
    packages=packages,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
        ],
    python_requires='>=3.6',
    install_requires=[
        "minecraft-launcher-lib @ git+https://github.com/BobDotCom/minecraft-launcher-lib/",
        "Flask",
        "requests",
        "click",
        "kivy"
    ],
    license='MIT',
    project_urls={
        'Documentation': 'https://mclauncher.readthedocs.io/en/latest/index.html',
        'Source':        'https://github.com/BobDotCom/mclauncher',
        'Tracker':       'https://github.com/BobDotCom/mclauncher/issues'
        },
    scripts=[
        'bin/mclauncher'
    ]
    )
