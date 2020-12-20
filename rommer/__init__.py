"""
Rommer is a tool for auditing ROMs and other binary files. It works by
computing checksums of your binary files, comparing them against databases
of known values from DAT files or other source.

Both databases and indexed binary files are stored in a persistent SQLite3
database, so that subsequent queries on the same files are fast.

rommer import <path> ...
- import DAT files beneath the given paths into the database

rommer scan <path> ...
- recursively index files and directories, storing metadata (checksums, length, last modified stamp)
- for compressed files: index the contents of each constituent file.

rommer report <path> ...
- report, for a list of files and set of DATs, which DATs are matched.

rommer copy <path> ...
- lean on 1g1r to generate 1G1R sets?
"""

import logging
import os
import sys

import hashlib
import pathlib
import zlib

from sqlalchemy import create_engine, Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

log = logging.getLogger(__name__)
Session = None


def find_files(paths, suffix=None):
    """
    Find all files at or beneath the given paths, of the specified suffix.
    :param paths: The paths to search for matching files.
    :param suffix: The file extension to which matches should be constrained.
    :return: A list of matching pathlib.Path objects.
    """
    # TODO: Handle suffix case-insensitively in a cross-platform way.
    # https://jdhao.github.io/2019/06/24/python_glob_case_sensitivity/
    files = []
    for path in paths:
        if not isinstance(path, pathlib.Path):
            path = pathlib.Path(path)
        if path.is_file():
            if suffix is None or path.suffix == suffix:
                files.append(path)
        else:
            glob = f'*.{suffix}' if suffix else '*'
            files.extend(f for f in path.rglob('*') if f.is_file())
    return files


def config_dir():
    """
    Get the location where rommer stores its configuration, notably the SQLite3
    database. To override it, set the ROMMER_CONFIG environment variable.
    """
    ROMMER_CONFIG = os.getenv('ROMMER_CONFIG')
    config_dir = pathlib.Path(ROMMER_CONFIG) if ROMMER_CONFIG else pathlib.Path.home() / '.config' / 'rommer'
    if not config_dir.exists():
        config_dir.mkdir()
    if not os.path.isdir(config_dir):
        raise f'Someone stole my config spot ({config_dir})'
    return config_dir


def session():
    """
    Create a session for interacting with the rommer database.
    The database is initialized and connected as needed.

    :return: a new SQLAlchemy Session object; for introduction to usage, see:
             https://docs.sqlalchemy.org/en/13/orm/session_basics.html#basics-of-using-a-session
    """
    global Session
    if Session:
        return Session.session()

    rommer_db_path = config_dir() / 'rommer.db'
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
        mtime = Column(Integer)
        size = Column(Integer)
        crc = Column(String)
        md5 = Column(String)
        sha1 = Column(String)

        def stat(self):
            return pathlib.Path(self.path).stat() if self.path else None

        def is_dirty(self, stat):
            # TODO: The below only tells us the file _might_ be dirty.
            # We should then recompute hashes and see if any changed.
            # If not, the file was merely touched, not modified.
            return self.size is None or self.mtime is None or \
                   self.size != stat.st_size or self.mtime < stat.st_mtime

        def calculate_checksums(self, recalc=False):
            if not self.path:
                raise Exception('Cannot calculate checksums without a path')

            stat = self.stat()
            if recalc or self.is_dirty(stat):
                self.size = stat.st_size
                self.mtime = stat.st_mtime
                self.crc = self.md5 = self.sha1 = None

            if not self.sha1 or not self.md5 or not self.crc:
                # Read file contents; we need to compute something from it.
                with open(self.path, 'rb') as fh:
                    b = fh.read()
                assert len(b) == self.size
                if not self.crc:
                    crc = hex(zlib.crc32(b))[2:]
                    self.crc = '0'*(8-len(crc)) + crc
                if not self.md5: self.md5 = hashlib.md5(b).hexdigest()
                if not self.sha1: self.sha1 = hashlib.sha1(b).hexdigest()

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

    Dat.games = relationship('Game', order_by=Game.id,
                             back_populates='dat',
                             cascade="all, delete, delete-orphan")


    global Rom
    class Rom(Base):
        """
        Metadata about a binary ROM file.
        """
        __tablename__ = 'roms'

        id = Column(Integer, primary_key=True)
        game_id = Column(Integer, ForeignKey('games.id'))

        name = Column(String)
        size = Column(Integer)
        crc = Column(String)
        md5 = Column(String)
        sha1 = Column(String)

        game = relationship('Game', back_populates='roms')

        def __repr__(self):
            return f"<Rom(game={self.game}, name='{self.name}'), size='{self.size}'), crc='{self.crc}'), md5='{self.md5}'), sha1='{self.sha1}')>"

    Game.roms = relationship('Rom', order_by=Rom.id,
                             back_populates='game',
                             cascade="all, delete, delete-orphan")


    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)

    return Session()
