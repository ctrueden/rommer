import logging
import os

from xml.dom.minidom import parse
from persist import *

log = logging.getLogger(__name__)

def cdata(el):
    return el.firstChild.wholeText

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

def parse_dat(datpath, dats):
    try:
        dom = parse(datpath)
    except:
        # Probably not an XML file.
        log.warning(f'Skipping unparseable file: {datpath}')
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
        category = datpath[datpath.rfind('/')+1:datpath.rfind('.')]
    assert category

    games = []
    games.extend(Game(el) for el in dom.getElementsByTagName('machine'))
    games.extend(Game(el) for el in dom.getElementsByTagName('game'))

    log.info(f'{category}: {len(games)} games / {sum(len(game.roms) for game in games)} roms')

    assert not category in dats
    dats[category] = games

def load_dats():
    dats = load('dat-cache.pickle')

    if dats:
        for category, games in dats.items():
            log.debug(f'{category}: {len(games)} games / {sum(len(game.roms) for game in games)} roms')
    else:
        log.info('Parsing DAT files')
        datdir = os.path.dirname(os.path.realpath(__file__))
        dats = {}
        for root, dirs, files in os.walk(datdir):
            datpaths = [os.path.join(root, f) for f in files if f.lower().endswith('.dat')]
            for datpath in datpaths:
                parse_dat(datpath, dats)

        log.info('Saving DATs to cache')
        save('dat-cache.pickle', dats)

    return dats
