==========
mclauncher
==========
A fully fledged launcher for Minecraft. Made in python, and supports almost all features of the official launcher. Not
tested on Windows.

Note
----
The ``mclauncher`` project name is currently not working. You can install mclauncher with pip, but you will have to use
the name ``pymclauncher`` until the project name is fixed. The command to run the launcher remains ``mclauncher``.

.. code-block:: bash

    pip install pymclauncher

    mclauncher -h


DISCLAIMER
----------
`This is not a cracked client/launcher!`

You will be required to authenticate with Microsoft to use this program. If you have not migrated your Mojang account to
Microsoft, you will be required to do so before using this program. If you would like to see the source code for the
backend authentication, you can find it `here <https://replit.com/@ScienceandTecha/mclauncher-backend>`_.

This being said, this program may not check to see if you have a valid account. It may be possible to launch a cracked
client using this program, but it is not recommended (It's against the terms of Minecraft to do so!). Hacked clients and
modded clients are fine.


Usage
-----

Install
~~~~~~~
Install ``mclauncher`` using your favorite flavor of the pip package manager.

.. code-block:: bash

    pip install mclauncher


Running
~~~~~~~
Use the help command to see a list of available commands. Pip should have added the ``mclauncher`` package to
PATH, so you should be able to simply run ``mclauncher`` in your terminal.

.. code-block:: bash

    mclauncher -h

If that doesn't work, a consistent fallback is to run ``mclauncher`` using your favorite flavor of the python command.

.. code-block:: bash

    python -m mclauncher -h