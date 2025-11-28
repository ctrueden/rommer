"""
Main entry point for the rommer command line tool.
"""

import argparse
import importlib
import logging
import pkgutil
import sys

import rommer.commands


def load_commands():
    commands = {}
    package = rommer.commands
    for loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
        full_name = package.__name__ + "." + name
        commands[name] = importlib.import_module(full_name)
    return commands


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    commands = load_commands()
    blurbs = []
    for name, command in commands.items():
        desc = f" {command.blurb}" if hasattr(command, "blurb") else ""
        blurbs.append(f"{name:<21}{desc}")
    blurbs.append("")
    blurbs.append("Run subcommand followed by -h flag for more detailed help.")

    parser = argparse.ArgumentParser(
        description="Wrangle your ROMs.", formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="verbose mode")
    subparsers = parser.add_subparsers(dest="subcommand", description="\n".join(blurbs))
    subparsers.required = True
    for name, command in commands.items():
        desc = f" {command.description}" if hasattr(command, "description") else None
        command.configure(subparsers.add_parser(name, description=desc))

    pargs = parser.parse_args(args)
    if pargs.verbose:
        logging.basicConfig(format="[%(levelname)s] %(message)s", level=logging.INFO)
    return commands[pargs.subcommand].run(pargs)


if __name__ == "__main__":
    sys.exit(main())
