import hashlib
import logging
import os
import pathlib
import pickle 
import sys
import zlib

from xml.dom.minidom import parse

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

datdir = os.path.dirname(os.path.realpath(__file__))

def mtime(path):
    return pathlib.Path(path).stat().st_mtime

# -- Data structures --

class File:
    def __init__(self, path):
        self.path = path
        with open(path, 'rb') as fh:
            b = fh.read()
        self.size = len(b)
        self.md5 = hashlib.md5(b).hexdigest()
        self.sha1 = hashlib.sha1(b).hexdigest()
        crc = hex(zlib.crc32(b))[2:]
        self.crc = '0'*(8-len(crc)) + crc
        self.mtime = mtime(path)

class Game:
    def __init__(self, el):
        self.name = el.getAttribute('name')
        self.description = cdata(el.getElementsByTagName('description')[0])
        self.roms = [Rom(child) for child in el.getElementsByTagName('rom')]

class Rom:
    def __init__(self, el):
        self.name = el.getAttribute('name')
        self.size = el.getAttribute('size')
        try:
            self.size = int(self.size)
        except:
            self.size = -1
        self.crc = el.getAttribute('crc')
        self.md5 = el.getAttribute('md5')
        self.sha1 = el.getAttribute('sha1')

# -- XML parsing functions --

def cdata(el):
    return el.firstChild.wholeText

def parse_dat(dat):
    try:
        dom = parse(dat)
    except:
        # Probably not an XML file.
        log.warning(f'Skipping unparseable file: {dat}')
        return

    category = None
    try:
        category = cdata(dom.getElementsByTagName('header')[0].getElementsByTagName('name')[0])
    except:
        pass
    if not category:
        try:
            category = cdata(dom.getElementsByTagName('header')[0].getElementsByTagName('listname')[0])
        except:
            pass
    if not category:
        # Use filename without extension.
        category = dat[dat.rfind('/')+1:dat.rfind('.')]
    assert category

    games = []
    games.extend(Game(el) for el in dom.getElementsByTagName('machine'))
    games.extend(Game(el) for el in dom.getElementsByTagName('game'))

    log.info(f'{category}: {len(games)} games / {sum(len(game.roms) for game in games)} roms')

    assert not category in data
    data[category] = games

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
            parse_dat(dat)

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
for category in matched_categories:
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
