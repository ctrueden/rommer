import logging
import os
import pickle 
import sys

from dats import *
from fileinfo import *
from persist import *

"""
Rommer is a tool for auditing ROMs and other binary files. It works by
computing and caching checksums of your binary files, comparing them against
databases of known values from [DAT files]() or other source.

desired actions from CLI and API:

rommer loaddats <path> ...
- recursively index DAT files, storing into an efficiently persisted structure.

rommer index <path> ...
- recursively index files and directories, storing metadata (checksums, length, last modified stamp)
- for compressed files: index the contents of each constituent file.

rommer report <path> ...
- report, for a list of files and set of DATs, which DATs are matched.

rommer copy <path> ...
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



Romulus
https://romulus.cc/
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

dats = load_dats()
fileinfos = load('fileinfo-cache.pickle')

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
save('fileinfo-cache.pickle', fileinfos)

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
