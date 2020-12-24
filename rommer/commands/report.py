import logging
import rommer

from sqlalchemy.orm import joinedload

log = logging.getLogger(__name__)

blurb = 'display DAT matches for the given path(s)'
description = 'Display DAT matches for the given path(s).'


def configure(parser):
    parser.add_argument('--have', action='store_true', help='print matched ROMs')
    parser.add_argument('--miss', action='store_true', help='print missing ROMs')
    parser.add_argument('--unmatched', action='store_true', help='print unmatched file paths')
    parser.add_argument('path', nargs='+', help='file paths to analyze')


def run(args):
    session = rommer.session()

    dat_count = session.query(rommer.Dat.id).count()
    if dat_count == 0:
        log.error('No DATs available. Use "rommer import" first to add some.')
        return 1

    # TODO: Probably this should be combined with scan.
    # For scanning, if the file is new, we add it...
    # And then we do the commit, and finally the big join query.

    log.info('Scanning for matches')
    files = set(str(file.resolve()) for file in rommer.find_files(args.path))
    matches = session.query(rommer.Rom, rommer.File) \
                     .filter(rommer.Rom.sha1 == rommer.File.sha1) \
                     .filter(rommer.Rom.md5 == rommer.File.md5) \
                     .filter(rommer.Rom.crc == rommer.File.crc) \
                     .filter(rommer.Rom.size == rommer.File.size)

    log.info('Filtering results')
    matched_files = set()
    matched_dats = set()
    matched_roms = {}
    count = 0
    for match in matches:
        file = match[1]
        count += 1
        if not file.path in files:
            continue
        matched_files.add(file.path)
        rom = match[0]
        if not rom.id in matched_roms:
            matched_roms[rom.id] = []
        matched_dats.add(rom.game.dat.id)
        matched_roms[rom.id].append(file.path)

    log.info('Calculating statistics')
    for dat_id in matched_dats:
        dat = session.query(rommer.Dat) \
                         .options(joinedload(rommer.Dat.games) \
                                 .joinedload(rommer.Game.roms)) \
                         .filter_by(id=dat_id).first()
        have = 0
        miss = 0
        for game in dat.games:
            for rom in game.roms:
                if rom.id in matched_roms:
                    have += 1
                    if args.have:
                        print(f'--> {rom.name} -> {matched_roms[rom.id]}')
                else:
                    miss += 1
                    if args.miss:
                        print(f'--> [MISSING] {rom.name}')
        if have > 0:
            total = have + miss
            percent = 100 * have / total
            print(f'{dat.name}: {have}/{total} ({percent}%)')

    print(f'Unmatched: {len(files) - len(matched_files)} / {len(files)}')
    if args.unmatched:
        for f in sorted(files.difference(matched_files)):
            print(f'--> {f}')
