import logging
import os
import sys

import hashlib
import os
import pathlib
import zlib

from sqlalchemy import create_engine, Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

"""
Rommer is a tool for auditing ROMs and other binary files. It works by
computing checksums of your binary files, comparing them against databases
of known values from DAT files or other source.

Both databases and indexed binary files are stored in a persistent SQLite3
database, so that subsequent queries on the same files are fast.

rommer import <path> ...
- recursively import DAT files, storing into an efficiently persisted structure.

rommer scan <path> ...
- recursively index files and directories, storing metadata (checksums, length, last modified stamp)
- for compressed files: index the contents of each constituent file.

rommer report <path> ...
- report, for a list of files and set of DATs, which DATs are matched.

rommer copy <path> ...
- lean on 1g1r to generate 1G1R sets?
"""

log = logging.getLogger(__name__)

Session = None

def session():
    global Session
    if Session:
        return Session.session()

    ROMMER_CONFIG = os.getenv('ROMMER_CONFIG')
    config_dir = pathlib.Path(ROMMER_CONFIG) if ROMMER_CONFIG else pathlib.Path.home() / '.config' / 'rommer'
    if not config_dir.exists():
        config_dir.mkdir()
    if not os.path.isdir(config_dir):
        raise f'Someone stole my config spot ({config_dir})'

    rommer_db_path = config_dir / 'rommer.db'

    engine = create_engine(f'sqlite:///{rommer_db_path}')

    Base = declarative_base()


    global File
    class File(Base):
        """
        Metadata about a binary file.
        """

        __tablename__ = 'files'

        id = Column(Integer, primary_key=True)

        path = Column(String)
        size = Column(Integer)
        mtime = Column(Integer)
        sha1 = Column(String)
        md5 = Column(String)
        crc = Column(String)

        def stat(self):
            return pathlib.Path(self.path).stat() if self.path else None

        def is_dirty(self, stat):
            return self.size is None or self.mtime is None or \
                   self.size != stat.st_size or self.mtime < stat.st_mtime

        def calculate_checksums(self, recalc=False):
            if not self.path:
                raise Exception('Cannot calculate checksums without a path')

            stat = self.stat()
            if recalc or self.is_dirty(stat):
                self.size = stat.st_size
                self.mtime = stat.st_mtime
                self.sha1 = self.md5 = self.crc = None

            if not self.sha1 or not self.md5 or not self.crc:
                # Read file contents; we need to compute something from it.
                with open(self.path, 'rb') as fh:
                    b = fh.read()
                assert len(b) == self.size
                if not self.md5: self.md5 = hashlib.md5(b).hexdigest()
                if not self.sha1: self.sha1 = hashlib.sha1(b).hexdigest()
                if not self.crc:
                    crc = hex(zlib.crc32(b))[2:]
                    self.crc = '0'*(8-len(crc)) + crc

        def __repr__(self):
            return f"<File(path='{self.path}', size={self.size}, mtime={self.mtime}, sha1={self.sha1}, md5={self.md5}, crc={self.crc})>"


    global Dat
    class Dat(Base):
        """
        A list of games.
        """
        __tablename__ = 'dats'

        id = Column(Integer, primary_key=True)
        file_id = Column(Integer, ForeignKey('files.id'))

        name = Column(String)
        description = Column(String)
        version = Column(String)
        date = Column(String)
        author = Column(String)
        url = Column(String)

        file = relationship('File')

        def __repr__(self):
            return f"<Dat(file={self.file}, name='{self.name}', description='{self.description}', version='{self.version}', date='{self.date}', author='{self.author}', url='{self.url}')>"


    global Game
    class Game(Base):
        """
        A list of roms.
        """
        __tablename__ = 'games'

        id = Column(Integer, primary_key=True)
        dat_id = Column(Integer, ForeignKey('dats.id'))

        name = Column(String)
        description = Column(String)

        dat = relationship('Dat', back_populates='games')

        def __repr__(self):
            return f"<Game(dat={self.dat}, name='{self.name}', description='{self.description}')>"

    Dat.games = relationship('Game', order_by=Game.id, back_populates='dat')


    global Rom
    class Rom(Base):
        """
        Metadata about a binary ROM file.
        """
        __tablename__ = 'roms'

        id = Column(Integer, primary_key=True)
        game_id = Column(Integer, ForeignKey('games.id'))
        file_id = Column(Integer, ForeignKey('files.id'))

        name = Column(String)

        game = relationship('Game', back_populates='roms')
        file = relationship('File')

        def __repr__(self):
            return f"<Rom(game={self.game}, name='{self.name}')>"

    Game.roms = relationship('Rom', order_by=Rom.id, back_populates='game')


    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)

    return Session()