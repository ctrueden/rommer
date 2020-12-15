import hashlib
import pathlib
import zlib

def cdata(el):
    return el.firstChild.wholeText

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
