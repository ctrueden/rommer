import logging

log = logging.getLogger(__name__)

blurb = 'display DAT matches for the given path(s)'
description = 'Display DAT matches for the given path(s).'


def configure(parser):
    parser.add_argument('path', nargs='+', help='file paths to analyze')


def run(args):
    print(f'run report: {args}')
    """
    log.info('Calculating auxiliary data structures')
    md5s = {}
    sha1s = {}
    crcs = {}
    category_for_game = {}
    game_for_rom = {}
    for category, games in dats.items():
        for game in games:
            category_for_game[game] = category
            for rom in game.roms:
                game_for_rom[rom] = game
                if rom.md5: md5s[rom.md5] = rom
                if rom.sha1: sha1s[rom.sha1] = rom
                if rom.crc: crcs[rom.crc] = rom

    log.info('Matching checksums')

    matches = {}
    unmatched = []

    for fileinfo in infos_to_analyze:
        rom = find_rom(fileinfo)
        if rom:
            matches[rom] = path
        else:
            unmatched.append(path)

    log.info('Calculating statistics')

    matched_categories = {category_for_game[game_for_rom[rom]] for rom in matches}
    for category in sorted(matched_categories):
        have = 0
        miss = 0
        for game in dats[category]:
            for rom in game.roms:
                if rom in matches:
                    have += 1
                else:
                    miss += 1
        if have > 0:
            total = have + miss
            percent = 100 * have / total
            print(f'{category}: {have}/{total} ({percent}%)')

    print(f'{len(unmatched)} unmatched')
    """
