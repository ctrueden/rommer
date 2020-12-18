from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md')) as f:
    rommer_long_description = f.read()

setup(
    name='rommer',
    version='0.1.0.dev0',
    author='Curtis Rueden',
    author_email='ctrueden@gmail.com',
    description='Organize your ROMs.',
    long_description=rommer_long_description,
    long_description_content_type='text/markdown',
    license='Public domain',
    url='https://github.com/ctrueden/rommer',
    packages=['rommer'],
    entry_points={
        'console_scripts': [
            'rommer=rommer.__main__:main'
        ]
    },
    install_requires=['sqlalchemy'],
    python_requires='>=3.6'
)
