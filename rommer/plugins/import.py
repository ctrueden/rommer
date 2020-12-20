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


def parse_dat(path, file=None):
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
    dat.file = file if file else rommer.File(path=path)
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
    return rommer.Rom(name=el.getAttribute('name'),
                      size=el.getAttribute('size'),
                      crc=el.getAttribute('crc'),
                      md5=el.getAttribute('md5'),
                      sha1=el.getAttribute('sha1'))


def run(args):
    session = rommer.session()

    log.info('Cataloging DAT files...')
    dats = []
    for datfile in rommer.find_files(args.path, '.dat'):
        datpath = str(datfile.resolve())
        existing_dat = None
        existing_file = session.query(rommer.File).filter_by(path=datpath).first()
        if existing_file:
            existing_dat = session.query(rommer.Dat).filter_by(file_id=existing_file.id).first()
        dats.append((datpath, existing_file, existing_dat))

    log.info('Importing DAT files...')
    for datpath, existing_file, existing_dat in dats:
        if existing_dat:
            if existing_file.is_dirty():
                # Delete DAT and reimport.
                log.info(f'Reimporting {datpath}...')
                session.delete(existing_dat)
            else:
                # DAT file has not changed; no action needed.
                log.info(f'Already imported: {datpath} -> {existing_dat.name}')
                continue
        else:
            log.info(f'Importing {datpath}...')

        # Import DAT.
        dat = parse_dat(datpath, existing_file)

        session.add(dat)
        session.commit()
        log.info(f'--> {dat.name}: {len(dat.games)} games / {sum(len(game.roms) for game in dat.games)} roms')

    log.info('Import complete.')
