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

import argparse
import json
import logging
import os
import socket
import subprocess
import sys
import webbrowser
from contextlib import closing

import minecraft_launcher_lib
import requests

from .pipe import LogPipe
from .webserver import run_server
from .ui import Gui, Cli

__version__ = "0.1.4"


def launch(gui: bool = False, args=None):
    # noinspection PyProtectedMember
    max_verbosity = int(max(logging._levelToName.keys()) / 10)
    parser = argparse.ArgumentParser()
    parser.add_argument("version", nargs="?", default=False, help="Minecraft version. Release versions and "
                                                                  "snapshots all work. Defaults to newest release.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--client", "-c", dest="client", default=False, metavar="name",
                       help="Use a custom client, such as OptiFine or Impact. Client name is NOT case sensitive. "
                            "(Warning: The client needs to be installed, the launcher won't automatically install "
                            "it.)")
    group.add_argument("--fabric", dest="fabric", nargs="?", default=False, const=True, metavar="version",
                       help="Use the fabric mod loader. Loader version is optional, defaults to newest release.")
    group.add_argument("--forge", dest="forge", nargs="?", default=False, const=True, metavar="version",
                       help="Use the forge mod loader. Loader version is optional, defaults to newest release.")
    parser.add_argument("-y", dest="y", default=False, action="store_true",
                        help="Bypass all prompts, automatically selecting yes for them.")
    parser.add_argument("--no-install", dest="no_install", default=False, action="store_true",
                        help="Don't run the install script at all, try to run locally installed version if "
                             "possible.")
    parser.add_argument('-v', dest="verbose", action='count', default=3,
                        help="Set verbosity. Can be supplied multiple times to increase verbosity, max "
                             f"{max_verbosity}. Defaults to 3. (1: Critical, 2: Error, 3: Warning, 4: Info, 5: Debug)")
    parser.add_argument('--version', "-V", action='version', version='%(prog)s ' + __version__)
    parser.add_argument('--manual-auth', "-m", dest="manual_auth", action="store_true", default=False,
                        help="Manually visit and paste url for authentication. When false, the script will create "
                             "a flask server on localhost, and automatically get the token after authenticating. "
                             "Defaults to false.")
    parser.add_argument("--gui", "-g", dest="gui", action="store_true",
                        default=False, help="Use a gui for the launching. Defaults to false.")
    if gui:
        class Args:
            verbose = 50
            gui = False
        args = Args
        ui = Gui()

        def ask_yes_no(text: str) -> bool:
            if args.y:
                return True
            while True:
                answer = input(text + " [y|n]")
                if answer.lower() == "y":
                    return True
                elif answer.lower() == "n":
                    return False
                else:
                    print("Please enter y or n")
    else:
        ui = Cli(parser)
        args = parser.parse_args(args)

        def ask_yes_no(text: str) -> bool:
            if args.y:
                return True
            return True

    if args.verbose > max_verbosity:
        ui.error(f"Verbosity level ({args.verbose}) exceeded max verbosity ({max_verbosity})")

    log_level = (max_verbosity + 1 - args.verbose) * 10

    # noinspection PyTypeChecker
    logging.basicConfig(level=log_level,
                        format="$asctime [$levelname] ($name): $message", style="$")

    logger = logging.getLogger(__name__)
    java_logger = logging.getLogger("minecraft")
    gui_logger = logging.getLogger("mclauncher_gui")

    # Set logging level for everything
    loggers = [logging.getLogger(name) for name in logging.root.manager.loggerDict]
    for logger in loggers:
        logger.setLevel(log_level)

    if False:  # if args.gui:
        # Gui disabled for now
        logger.info("Running gui")
        launch(gui=True)
        return
    if gui:
        os.environ['KIVY_NO_ARGS'] = "1"
        from .ui import gui
        app = gui.prep()()
        app.run()
    if args.gui:
        parser.error("GUI mode is disabled for now.")

    # Quick intro
    print("If no further input is required, you will be prompted to login momentarily.")

    def forge(vanilla_version, java_path, mc_directory):
        if args.forge is not True:
            forge_version = vanilla_version + "-forge-" + args.forge
        else:
            # Get latest version
            forge_version = minecraft_launcher_lib.forge.find_forge_version(vanilla_version)
        # Checks if a forge version exists for that version
        if forge_version is None:
            print("This Minecraft version is not supported by forge")
            return
        if len([x for x in minecraft_launcher_lib.utils.get_installed_versions(mc_directory) if
                x['id'] == forge_version.replace("-forge-", "\\").replace("-", "-forge-").replace("\\", "-forge-")][
               :1]) > 0:
            if ask_yes_no(f"Forge version {forge_version} is installed. Would you like to use it?"):
                return
                # Checks if the version can be installed automatic
        if minecraft_launcher_lib.forge.supports_automatic_install(forge_version):
            if ask_yes_no(f"Do you want to install forge {forge_version}?"):
                if ask_yes_no(f"Use auto install?"):
                    mc_directory = minecraft_launcher_lib.utils.get_minecraft_directory()
                    callback = {
                        "setStatus": lambda text: print(text)
                    }
                    minecraft_launcher_lib.forge.install_forge_version(forge_version, mc_directory,
                                                                       callback=callback, java=java_path)
                else:
                    minecraft_launcher_lib.forge.run_forge_installer(forge_version, java_path)
        else:
            print(f"Forge {forge_version} can't be installed automatic.")
            if ask_yes_no("Do you want to run the installer?"):
                minecraft_launcher_lib.forge.run_forge_installer(forge_version, java_path)

    def fabric(vanilla_version, java_path, mc_directory):
        if not minecraft_launcher_lib.fabric.is_minecraft_version_supported(vanilla_version):
            print("This version is not supported by fabric")
            return vanilla_version

        if args.fabric is not True:
            loader_version = args.fabric
        else:
            loader_version = minecraft_launcher_lib.fabric.get_latest_loader_version()

        fabric_version = "fabric-loader-" + loader_version + "-" + vanilla_version
        print(fabric_version)

        if len([x for x in minecraft_launcher_lib.utils.get_installed_versions(mc_directory) if
                x['id'] == fabric_version][:1]) > 0:
            if ask_yes_no(f"Fabric version {loader_version} is installed. Would you like to use it?"):
                return fabric_version

        if ask_yes_no(f"Do you want to install fabric {loader_version}?"):
            callback = {
                "setStatus": lambda text: print(text)
            }
            minecraft_launcher_lib.fabric.install_fabric(vanilla_version, mc_directory, callback=callback,
                                                         java=java_path)
            return fabric_version
        return vanilla_version

    def client(vanilla_version, client_name, mc_directory):
        versions = os.listdir(mc_directory + "/versions")
        release_versions = [version for version in versions if vanilla_version in version]
        client_versions = [version for version in versions if client_name.lower() in version.lower()]
        possible_versions = [version for version in release_versions if version in client_versions]
        if len(possible_versions) == 0:
            if ask_yes_no(
                    f"Couldn't find a suitable version for \"{client_name}\" with MC \"{vanilla_version}\". "
                    f"Would you like to try to run vanilla minecraft for \"{vanilla_version}\"?"):
                return vanilla_version
            else:
                parser.exit(0)
        elif len(possible_versions) > 1:
            ui.error(f"Found multiple versions for \"{client_name}\" with MC \"{vanilla_version}\". Versions found: \""
                     + '", "'.join(possible_versions) + '"')
        else:
            return possible_versions[0]

    if args.version:
        latest_version = args.version
        logger.debug(f"Using provided version {latest_version}")
    else:
        # Get latest version
        latest_version = minecraft_launcher_lib.utils.get_latest_version()["release"]
        logger.debug(f"Using fetched version {latest_version}")

    # Get Minecraft directory
    minecraft_directory = minecraft_launcher_lib.utils.get_minecraft_directory()
    logger.debug(f"Found minecraft directory at {minecraft_directory}")

    # Make sure version is valid
    if not minecraft_launcher_lib.utils.is_version_valid(latest_version, minecraft_directory):
        ui.error("Invalid version!")

    if not args.no_install:
        logger.info(f"Installing {latest_version}")
        # Make sure, the latest version of Minecraft is installed
        minecraft_launcher_lib.install.install_minecraft_version(latest_version, minecraft_directory)
    else:
        logger.info(f"Skipping install of {latest_version}")

    if args.fabric is not False:
        logger.info("Using fabric client")
        java = minecraft_launcher_lib.command.get_minecraft_command(latest_version, minecraft_directory, {})[0]
        logger.debug(f"Found java_path at {java}")
        latest_version = fabric(latest_version, java, minecraft_directory)
        logger.debug(f"Finished fabric injection and changed version to {latest_version}")

    if args.forge is not False:
        java = minecraft_launcher_lib.command.get_minecraft_command(latest_version, minecraft_directory, {})[0]

        forge(latest_version, java, minecraft_directory)
        latest_version = minecraft_launcher_lib.forge.find_forge_version(latest_version)
        latest_version = latest_version.replace("-forge-", "\\").replace("-", "-forge-").replace("\\", "-forge-")

    if args.client is not False:
        latest_version = client(latest_version, args.client, minecraft_directory)

    def find_free_port():
        # Finds a random open port to assign the webserver to.
        with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
            s.bind(('', 0))
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            return s.getsockname()[1]

    # Login
    redirect_url = 'https://mclauncher.bobdotcom.xyz/authorize'
    client_id = "d83138ec-c608-4b87-959d-0b228f218bb3"
    port = find_free_port()
    login_url = minecraft_launcher_lib.microsoft_account.get_login_url(client_id, redirect_url).replace("<optional;",
                                                                                                        str(port))

    if not args.manual_auth:
        # Setup webserver
        def wrapper():
            webbrowser.open_new(login_url)
        auth_code = run_server(when_ready=wrapper, port=port, log_level=logger.getEffectiveLevel())

    else:
        print(f"Please open {login_url} in your browser and copy the url you are redirected into the prompt below.")
        code_url = input()

        # Check if the url contains a code
        if not minecraft_launcher_lib.microsoft_account.url_contains_auth_code(code_url):
            print("That url is not valid")
            sys.exit(1)

        # Get the code from the url
        auth_code = minecraft_launcher_lib.microsoft_account.get_auth_code_from_url(code_url)

    # Get the login data
    req = requests.post("https://mclauncher.bobdotcom.xyz/authorize", data={"code": auth_code})
    login_data = req.json()

    game_dir = None

    launcher_profiles = os.path.join(minecraft_directory, "launcher_profiles.json")
    if os.path.exists(launcher_profiles):
        with open(launcher_profiles, "r") as f:
            data = json.load(f)
        if data.get("profiles"):
            profiles = data["profiles"]
            for v in profiles.values():
                if v.get("lastVersionId") == latest_version:
                    logger.info(f"Found profile in launcher profiles for {latest_version}")
                    game_dir = v.get("gameDir")
                    break

    # Get Minecraft command
    minecraft_command = minecraft_launcher_lib.command.get_minecraft_command(latest_version, minecraft_directory,
                                                                             login_data)

    if game_dir is not None:
        minecraft_command[minecraft_command.index("--gameDir") + 1] = game_dir

    if minecraft_command[0] == "java":
        path = os.path.join(minecraft_directory, "runtime", "jre-legacy",
                            "mac-os", "jre-legacy", "jre.bundle", "Contents", "Home", "bin")
        if os.path.exists(os.path.join(path, "java")):
            minecraft_command[0] = os.path.join(path, "java")
        elif os.path.exists(os.path.join(path, "java_path")):
            minecraft_command[0] = os.path.join(path, "java_path")

    logger.debug(f"Running command: {' '.join(minecraft_command)}")

    def announce(message):
        print(f"{message}\n{'=' * len(message)}\n")

    # Start Minecraft
    announce("Starting minecraft")
    logpipe = LogPipe(java_logger)

    # noinspection PyTypeChecker
    with subprocess.Popen(minecraft_command, stdout=logpipe, stderr=logpipe) as _:
        logpipe.close()


if __name__ == "__main__":
    launch()
