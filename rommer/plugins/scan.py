import logging

log = logging.getLogger(__name__)

blurb = 'compute checksums for the given file path(s)'
description = 'Scan the given file path(s), compute and caching checksums.'


def configure(parser):
    parser.add_argument('path', nargs='+', help='file path to scan')


"""
def is_match(key, dictionary, size):
    if key in dictionary:
        rom = dictionary[key]
        if rom.size == size:
            return rom


def find_rom(fileinfo):
    return is_match(fileinfo.md5,  md5s,  fileinfo.size) or \
           is_match(fileinfo.sha1, sha1s, fileinfo.size) or \
           is_match(fileinfo.crc,  crcs,  fileinfo.size)
"""

def run(args):
    print(f'run scan: {args}')

"""
    dats = load_dats()
    fileinfos = load('fileinfo.cache')

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
    save('fileinfo.cache', fileinfos)
"""
