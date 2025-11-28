import logging
import os
import rommer

from tqdm import tqdm
from xml.dom.minidom import parse

log = logging.getLogger(__name__)

blurb = "scan and import DATs"
description = "Scan for DATs and import them to the rommer database."


def configure(parser):
    parser.add_argument("path", nargs="+", help="file path to search for DATs")


def cdata(root, tag):
    els = root.getElementsByTagName(tag)
    return els[0].firstChild.wholeText if els else None


def parse_dat(path, file=None):
    try:
        dom = parse(path)
    except Exception:
        # Probably not an XML file.
        log.warning(f"Skipping unparseable file: {path}")
        return None

    name = listname = description = version = date = author = url = None
    try:
        header = dom.getElementsByTagName("header")[0]
        name = cdata(header, "name")
        listname = cdata(header, "listname")
        description = cdata(header, "description")
        version = cdata(header, "version")
        date = cdata(header, "date")
        author = cdata(header, "author")
        url = cdata(header, "url")
    except Exception:
        pass

    name_no_ext = path[path.rfind("/") + 1 : path.rfind(".")]

    dat = rommer.Dat(
        name=name or listname or name_no_ext,
        description=description,
        version=version,
        date=date,
        author=author,
        url=url,
    )
    dat.file = file if file else rommer.File(path=path)
    dat.file.calculate_checksums()
    dat.games.extend(game(el) for el in dom.getElementsByTagName("machine"))
    dat.games.extend(game(el) for el in dom.getElementsByTagName("game"))

    return dat


def game(el):
    game = rommer.Game(
        name=el.getAttribute("name"), description=cdata(el, "description")
    )
    game.roms.extend([rom(child) for child in el.getElementsByTagName("rom")])
    return game


def rom(el):
    return rommer.Rom(
        name=el.getAttribute("name"),
        size=el.getAttribute("size"),
        crc=el.getAttribute("crc"),
        md5=el.getAttribute("md5"),
        sha1=el.getAttribute("sha1"),
    )


def run(args):
    session = rommer.session()

    datfile_list = list(rommer.find_files(args.path, ".dat"))
    datpaths = [str(f.resolve()) for f in datfile_list]

    # Bulk queries: fetch all existing files and dats at once.
    verbose = log.isEnabledFor(logging.INFO)
    existing_files = (
        session.query(rommer.File).filter(rommer.File.path.in_(datpaths)).all()
    )
    existing_files_map = {f.path: f for f in existing_files}

    file_ids = [f.id for f in existing_files]
    existing_dats = (
        session.query(rommer.Dat).filter(rommer.Dat.file_id.in_(file_ids)).all()
    )
    existing_dats_map = {d.file_id: d for d in existing_dats}

    dats = []
    for datfile in tqdm(
        datfile_list, desc="Cataloging DAT files", unit="file", disable=None
    ):
        datpath = str(datfile.resolve())
        existing_file = existing_files_map.get(datpath)
        existing_dat = (
            existing_dats_map.get(existing_file.id) if existing_file else None
        )
        dats.append((datpath, existing_file, existing_dat))

    pending_rows = 0
    with tqdm(dats, desc="Importing DAT files", unit="file", disable=None) as pbar:
        for datpath, existing_file, existing_dat in pbar:
            # Update progress bar with current DAT name
            filename = os.path.basename(datpath)
            pbar.set_postfix_str(filename[:40])

            if existing_dat:
                if existing_file.is_dirty():
                    # Delete DAT and reimport.
                    rommer.vlog(f"Reimporting {datpath}...", verbose)
                    session.delete(existing_dat)
                else:
                    # DAT file has not changed; no action needed.
                    rommer.vlog(
                        f"Already imported: {datpath} -> {existing_dat.name}", verbose
                    )
                    continue
            else:
                rommer.vlog(f"Importing {datpath}...", verbose)

            # Import DAT.
            dat = parse_dat(datpath, existing_file)
            if dat is None:
                continue
            game_count = len(dat.games)
            rom_count = sum(len(game.roms) for game in dat.games)
            pending_rows += 1 + game_count + rom_count
            session.add(dat)
            rommer.vlog(
                f"--> {dat.name}: {game_count} games / {rom_count} roms", verbose
            )

            if pending_rows >= 10000:
                # Avoid transactions getting too large.
                session.commit()
                pending_rows = 0

    session.commit()
    rommer.vlog("Import complete.", verbose)
