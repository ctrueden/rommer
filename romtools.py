import logging
import os
import pickle 
import sys

from datastructures import *
from datparse import *

"""
desired actions from CLI and API:
- recursively index DAT files, storing into an efficiently persisted structure.
- recursively index files and directories, storing metadata (checksums, length, last modified stamp)
- for compressed files: index the contents of each constituent file.
- report, for a list of files and set of DATs, which DATs are matched.
- lean on 1g1r to generate 1G1R sets?

class Dat(list)
def import(path)
TDD for API

class Dats(list)
def load(path)
def find(FileInfo)

class FileIndex(dict)? {str: FileInfo}
def scan(path)

class FileInfo [as File below]
"""

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# -- Hash matching functions --

def is_match(key, dictionary, size):
    if key in dictionary:
        rom = dictionary[key]
        if rom.size == size:
            return rom

def find_rom(fileinfo):
    return is_match(fileinfo.md5,  md5s,  fileinfo.size) or \
           is_match(fileinfo.sha1, sha1s, fileinfo.size) or \
           is_match(fileinfo.crc,  crcs,  fileinfo.size)

# -- Main --

datdir = os.path.dirname(os.path.realpath(__file__))

try:
    with open('data.cache', 'rb') as cache:
        log.info('Loading DATs from cache')
        data = pickle.load(cache)
    for category, games in data.items():
        log.debug(f'{category}: {len(games)} games / {sum(len(game.roms) for game in games)} roms')
except:
    log.info('Parsing DAT files')
    data = {}
    for root, dirs, files in os.walk(datdir):
        dats = [os.path.join(root, f) for f in files if f.lower().endswith('.dat')]
        for dat in dats:
            parse_dat(dat, data)

    log.info('Saving DATs to cache')
    with open('data.cache', 'wb') as cache:
        pickle.dump(data, cache)
    pass

try:
    with open('fileinfo.cache', 'rb') as cache:
        log.info('Loading file metadata from cache')
        fileinfos = pickle.load(cache)
except:
    fileinfos = {}

log.info('Calculating checksums')

infos_to_analyze = []
for d in sys.argv[1:]:
    for root, dirs, files in os.walk(d):
        for f in files:
            if f.lower().endswith('.zip') or f.lower().endswith('.7z'):
                log.warning(f'Skipping compressed file: {f}')
                continue
            path = os.path.join(root, f)
            if path in fileinfos and mtime(path) == fileinfos[path].mtime:
                fileinfo = fileinfos[path]
            else:
                fileinfo = File(path)
                fileinfos[path] = fileinfo
            infos_to_analyze.append(fileinfo)

log.info('Saving file metadata to cache')

with open('fileinfo.cache', 'wb') as cache:
    pickle.dump(fileinfos, cache)

log.info('Calculating auxiliary data structures')
md5s = {}
sha1s = {}
crcs = {}
category_for_game = {}
game_for_rom = {}
for category, games in data.items():
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
    for game in data[category]:
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
