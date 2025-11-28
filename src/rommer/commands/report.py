import logging
import os
import rommer
import time

from sqlalchemy.orm import joinedload
from tqdm import tqdm

log = logging.getLogger(__name__)

blurb = "display DAT matches for the given path(s)"
description = "Display DAT matches for the given path(s)."


def configure(parser):
    parser.add_argument("--have", action="store_true", help="print matched ROMs")
    parser.add_argument("--miss", action="store_true", help="print missing ROMs")
    parser.add_argument(
        "--unmatched", action="store_true", help="print unmatched file paths"
    )
    parser.add_argument("path", nargs="+", help="file paths to analyze")


def run(args):
    session = rommer.session()

    dat_count = session.query(rommer.Dat.id).count()
    if dat_count == 0:
        log.error('No DATs available. Use "rommer import" first to add some.')
        return 1

    file_list = list(rommer.find_files(args.path))
    files = []
    verbose = log.isEnabledFor(logging.INFO)
    for file in tqdm(file_list, desc="Cataloging files", unit="file", disable=None):
        path = str(file.resolve())
        existing_file = session.query(rommer.File).filter_by(path=path).first()
        files.append((path, existing_file))

    then = time.time()
    with tqdm(files, desc="Scanning files", unit="file", disable=None) as pbar:
        for path, existing_file in pbar:
            # Update progress bar with current file name
            filename = os.path.basename(path)
            pbar.set_postfix_str(filename[:40])

            if existing_file:
                rommer.vlog(f"Updating {path}...", verbose)
                existing_file.calculate_checksums()
            else:
                rommer.vlog(f"Processing {path}...", verbose)
                file = rommer.File(path=path)
                file.calculate_checksums()
                session.add(file)
                rommer.vlog(
                    f"--> {file.path}: size={file.size}, sha1={file.sha1}, md5={file.md5}, crc={file.crc}",
                    verbose,
                )

            now = time.time()
            if now - then > 10:
                # Flush transaction every ~10 seconds.
                rommer.vlog("Committing to DB...", verbose)
                session.commit()
                then = now

    rommer.vlog("Committing to DB...", verbose)
    session.commit()

    log.info("Scanning for matches")
    files = set(str(file.resolve()) for file in rommer.find_files(args.path))
    matches = (
        session.query(rommer.Rom, rommer.File)
        .filter(rommer.Rom.sha1 == rommer.File.sha1)
        .filter(rommer.Rom.md5 == rommer.File.md5)
        .filter(rommer.Rom.crc == rommer.File.crc)
        .filter(rommer.Rom.size == rommer.File.size)
    )

    log.info("Filtering results")
    matched_files = set()
    matched_dats = set()
    matched_roms = {}
    count = 0
    for match in matches:
        file = match[1]
        count += 1
        if file.path not in files:
            continue
        matched_files.add(file.path)
        rom = match[0]
        if rom.id not in matched_roms:
            matched_roms[rom.id] = []
        matched_dats.add(rom.game.dat.id)
        matched_roms[rom.id].append(file.path)

    log.info("Calculating statistics")
    for dat_id in matched_dats:
        dat = (
            session.query(rommer.Dat)
            .options(joinedload(rommer.Dat.games).joinedload(rommer.Game.roms))
            .filter_by(id=dat_id)
            .first()
        )
        have = 0
        miss = 0
        for game in dat.games:
            for rom in game.roms:
                if rom.id in matched_roms:
                    have += 1
                else:
                    miss += 1
        if have > 0:
            total = have + miss
            percent = 100 * have / total
            print(f"{dat.name}: {have}/{total} ({percent}%)")

        if args.have or args.miss:
            for game in dat.games:
                for rom in game.roms:
                    match = rom.id in matched_roms
                    if args.have and match:
                        print(f"--> {rom.name} -> {matched_roms[rom.id]}")
                    if args.miss and not match:
                        print(f"--> [MISSING] {rom.name}")

    print(f"Unmatched: {len(files) - len(matched_files)} / {len(files)}")
    if args.unmatched:
        for f in sorted(files.difference(matched_files)):
            print(f"--> {f}")
