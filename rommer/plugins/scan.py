import logging
import rommer
import time

log = logging.getLogger(__name__)

blurb = 'compute checksums for the given file path(s)'
description = 'Scan the given file path(s), compute and caching checksums.'


def configure(parser):
    parser.add_argument('path', nargs='+', help='file path to scan')


def run(args):
    session = rommer.session()

    log.info('Cataloging files...')
    files = []
    for file in rommer.find_files(args.path):
        path = str(file.resolve())
        existing_file = session.query(rommer.File).filter_by(path=path).first()
        files.append((path, existing_file))

    log.info('Scanning files...')
    then = time.time()
    for path, existing_file in files:
        if existing_file:
            log.info(f'Updating {path}...')
            existing_file.calculate_checksums()
        else:
            log.info(f'Processing {path}...')
            file = rommer.File(path=path)
            file.calculate_checksums()
            session.add(file)
            log.info(f'--> {file.path}: size={file.size}, sha1={file.sha1}, md5={file.md5}, crc={file.crc}')
        now = time.time()
        if now - then > 10:
            # Flush transaction every ~10 seconds.
            log.info('Committing to DB...')
            session.commit()
            then = now

    log.info('Committing to DB...')
    session.commit()
    log.info('Scan complete.')
