"""
Download and update DAT files from various sources.

This command downloads DAT files from configured sources (TOSEC, No-Intro,
Redump, MAME, etc.) and optionally imports them into the rommer database.
"""

import logging
import pathlib

# TODO: Implement source plugins
# import rommer.sources

log = logging.getLogger(__name__)

blurb = "download DAT files from online sources"
description = """Download DAT files from online sources.

Supported sources:
- tosec: TOSEC (The Old School Emulation Center)
- no-intro: No-Intro cartridge preservation project
- redump: Redump disc preservation project
- mame: MAME arcade ROM database
- opengood: OpenGood (GoodTools historical preservation, 35 platforms)

DAT files are cached in ~/.local/share/rommer/dats/ (or $ROMMER_DATA).
Use --import to automatically import downloaded DATs into the database.
"""


def configure(parser):
    parser.add_argument(
        "--source",
        action="append",
        choices=["tosec", "no-intro", "redump", "mame", "opengood", "all"],
        help="DAT source(s) to update (can specify multiple times)",
    )
    parser.add_argument(
        "--list-sources", action="store_true", help="list available DAT sources"
    )
    parser.add_argument(
        "--import",
        dest="do_import",
        action="store_true",
        help="automatically import downloaded DATs",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="show what would be downloaded without downloading",
    )


def data_dir():
    """
    Get the location where rommer stores downloaded DAT files.
    To override it, set the ROMMER_DATA environment variable.
    """
    import os

    ROMMER_DATA = os.getenv("ROMMER_DATA")
    data_dir = (
        pathlib.Path(ROMMER_DATA)
        if ROMMER_DATA
        else pathlib.Path.home() / ".local" / "share" / "rommer"
    )
    dats_dir = data_dir / "dats"
    if not dats_dir.exists():
        dats_dir.mkdir(parents=True)
    if not dats_dir.is_dir():
        raise Exception(f"Someone stole my data spot ({dats_dir})")
    return dats_dir


def run(args):
    """
    Main entry point for the update command.

    TODO: Implement the following:
    1. Load source plugins from rommer.sources
    2. Determine which sources to update (from args.source or all)
    3. For each source:
       a. Check if update is needed (version comparison)
       b. Download DAT files (with progress indication)
       c. Extract/organize files in data_dir()
       d. Update version metadata in database
    4. If args.do_import: call import command on new DATs
    5. Handle errors gracefully (don't fail all sources if one fails)
    """

    if args.list_sources:
        print("Available DAT sources:")
        print("  tosec      - TOSEC (The Old School Emulation Center)")
        print("  no-intro   - No-Intro cartridge preservation project")
        print("  redump     - Redump disc preservation project")
        print("  mame       - MAME arcade ROM database")
        print("  opengood   - OpenGood (GoodTools April 2016 snapshot, 35 platforms)")
        print()
        print("Note: OpenGood is historical preservation (not updated since 2016)")
        print("      but valuable for matching older ROM dumps.")
        print()
        print("Configure sources in ~/.config/rommer/sources.conf")
        return 0

    log.error("The 'update' command is not yet implemented.")
    log.info("See update-datfiles.sh for a partial implementation.")
    log.info("Run 'rommer update --list-sources' for planned sources.")
    return 1
