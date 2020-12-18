import logging
import os
import rommer

from xml.dom.minidom import parse

log = logging.getLogger(__name__)

blurb = 'scan and import DATs'
description = 'Scan for DATs and import them to the rommer database.'


def configure(parser):
    parser.add_argument('path', nargs='+', help='file path to search for DATs')


def cdata(root, tag):
    els = root.getElementsByTagName(tag)
    return els[0].firstChild.wholeText if els else None


def parse_dat(path):
    try:
        dom = parse(path)
    except:
        # Probably not an XML file.
        log.warning(f'Skipping unparseable file: {path}')
        return None

    name = listname = description = version = date = author = url = None
    try:
        header = dom.getElementsByTagName('header')[0]
        name = cdata(header, 'name')
        listname = cdata(header, 'listname')
        description = cdata(header, 'description')
        version = cdata(header, 'version')
        date = cdata(header, 'date')
        author = cdata(header, 'author')
        url = cdata(header, 'url')
    except:
        pass

    name_no_ext = path[path.rfind('/')+1:path.rfind('.')]

    dat = rommer.Dat(name=name or listname or name_no_ext,
                     description=description,
                     version=version,
                     date=date,
                     author=author,
                     url=url)
    dat.file = rommer.File(path=path)
    dat.file.calculate_checksums()
    dat.games.extend(game(el) for el in dom.getElementsByTagName('machine'))
    dat.games.extend(game(el) for el in dom.getElementsByTagName('game'))

    return dat


def game(el):
    game = rommer.Game(name=el.getAttribute('name'),
                       description=cdata(el, 'description'))
    game.roms.extend([rom(child) for child in el.getElementsByTagName('rom')])
    return game


def rom(el):
    file = rommer.File(size=el.getAttribute('size'),
                       sha1=el.getAttribute('sha1'),
                       md5=el.getAttribute('md5'),
                       crc=el.getAttribute('crc'))
    return rommer.Rom(file=file, name=el.getAttribute('name'))


def run(args):
    log.info('Connecting to DB...')
    session = rommer.session()

    log.info('Scanning for DAT files...')
    datpaths_to_parse = []
    for path in args.path:
        for root, dirs, files in os.walk(path):
            datpaths = [os.path.join(root, f) for f in files if f.lower().endswith('.dat')]
            for datpath in datpaths:
                # TODO: fix to always use absolute path
                existing_file = session.query(rommer.File).filter_by(path=datpath).first()
                if existing_file:
                    existing_dat = session.query(rommer.Dat).filter_by(file_id=existing_file.id).first()
                    if existing_dat:
                        # TODO: reparse if file is dirty
                        log.info(f'Already imported: {datpath} -> {existing_dat.name}')
                        continue
                datpaths_to_parse.append(datpath)

    for datpath in datpaths_to_parse:
        log.info(f'Importing {datpath}...')
        dat = parse_dat(datpath)
        if dat:
            session.add(dat)
            session.commit()
            log.info(f'--> {dat.name}: {len(dat.games)} games / {sum(len(game.roms) for game in dat.games)} roms')

    log.info('Import complete.')
