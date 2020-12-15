import logging

from xml.dom.minidom import parse

from datastructures import *

log = logging.getLogger(__name__)

def parse_dat(dat, data):
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

