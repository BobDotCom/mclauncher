import codecs
import os.path
import re

import setuptools


def read(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, rel_path), 'r') as fp:
        return fp.read()


def exists(rel_path):
    here = os.path.abspath(os.path.dirname(__file__))
    return os.path.exists(os.path.join(here, rel_path))


if exists("name.txt"):
    project_name = (read("name.txt").splitlines() + [""])[0].strip()
else:
    project_name = "mclauncher"

requirements = read('requirements.txt').splitlines()

version = ''

# The full version, including alpha/beta/rc tags
with open('mclauncher/__init__.py') as f:
    search = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE)

    if search is not None:
        version = search.group(1)

    else:
        raise RuntimeError("Could not grab version string")

if not version:
    raise RuntimeError('version is not set')

if version.endswith(('a', 'b', 'rc')):
    # append version identifier based on commit count
    try:
        import subprocess
        p = subprocess.Popen(['git', 'rev-list', '--count', 'HEAD'],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if out:
            version += out.decode('utf-8').strip()
        p = subprocess.Popen(['git', 'rev-parse', '--short', 'HEAD'],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = p.communicate()
        if out:
            version += '+g' + out.decode('utf-8').strip()
    except Exception:
        pass

with open("README.rst", "r") as fh:
    long_description = fh.read()

packages = [
    "mclauncher",
    "mclauncher.ui"
]

setuptools.setup(
    name=project_name,
    version=version,
    author="BobDotCom",
    author_email="bobdotcomgt@gmail.com",
    description="A minecraft launcher made in python.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/BobDotCom/mclauncher",
    download_url='https://github.com/BobDotCom/mclauncher/releases',
    packages=packages,
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
        ],
    python_requires='>=3.6',
    install_requires=requirements,
    license='MIT',
    project_urls={
        'Documentation': 'https://mclauncher.readthedocs.io/en/latest/index.html',
        'Source':        'https://github.com/BobDotCom/mclauncher',
        'Tracker':       'https://github.com/BobDotCom/mclauncher/issues'
        },
    scripts=[
        'mclauncher/bin/mclauncher'
    ]
    )
