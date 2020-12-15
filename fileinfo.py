import hashlib
import pathlib
import zlib

def mtime(path):
    return pathlib.Path(path).stat().st_mtime

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
