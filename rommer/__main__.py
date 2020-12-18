import argparse
import importlib
import logging
import pkgutil
import sys

import rommer.plugins


def load_plugins():
    plugins = {}
    package = rommer.plugins
    for loader, name, is_pkg in pkgutil.walk_packages(package.__path__):
        full_name = package.__name__ + '.' + name
        plugins[name] = importlib.import_module(full_name)
    return plugins


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    plugins = load_plugins()
    blurbs = []
    for name, plugin in plugins.items():
        desc = f' {plugin.blurb}' if hasattr(plugin, 'blurb') else ''
        blurbs.append(f'{name:<21}{desc}')
    blurbs.append('')
    blurbs.append('Run subcommand followed by -h flag for more detailed help.')

    parser = argparse.ArgumentParser(description='Wrangle your ROMs.',
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('-v', '--verbose', action='store_true', help='verbose mode')
    subparsers = parser.add_subparsers(dest="subcommand", description="\n".join(blurbs))
    subparsers.required = True
    for name, plugin in plugins.items():
        desc = f' {plugin.description}' if hasattr(plugin, 'description') else Non
        plugin.configure(subparsers.add_parser(name, description=desc))

    pargs = parser.parse_args(args)
    if pargs.verbose:
        logging.basicConfig(format='[%(levelname)s] %(message)s', level=logging.INFO)
    return plugins[pargs.subcommand].run(pargs)


if __name__ == "__main__":
    sys.exit(main())
