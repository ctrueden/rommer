import collections
import itertools
import logging
import rommer
import time

log = logging.getLogger(__name__)

blurb = 'compute similarity of binary files'
description = '''Compare files for matching byte sequences.

The command prints a similarity percentage between every pair of input files.

Each byte-triple is interpreted as an integer value in range(0, 2**24):

    ABC, BCD, CDE, DEF, EFG, FGH, GHI, HIJ, IJK, JKL, etc.

These values are counted, then hashed with their adjacent triple:

    ABC, BCD, CDE, DEF, EFG, FGH, GHI, etc.
    ^^^            ^^^
     \--------------/
            |
           A-F, B-G, C-H, D-I, E-J, F-K, G-L, etc.

These combined 24-bit values are then counted and merged again:

           A-F, B-G, C-H, D-I, E-J, F-K, G-L, etc.
           ^^^                           ^^^
            \-----------------------------/
                           |
                          A-L, B-M, C-N, etc.

And so on until each hashed value spans more than 50% of the file,
at which point the process cannot continue.
'''


def configure(parser):
    parser.add_argument('path', nargs='+', help='file path to compare')


def _count_blocks(values, counts, spread):
    # TODO: Count higher-spread aggregate values with more weight.
    # The question is: how much more?
    counts.update(values)
    if len(values) <= spread:
        return

    # Merge adjacent values and recurse
    nv = []
    for i in range(len(values) - spread):
        # TODO: Improve hash combine function. Result must be in [0, 2**24).
        # But much better would be for (a, b) != (b, a).
        nv.append(values[i] ^ values[i+spread])
    _count_blocks(nv, counts, spread * 2)


def count_blocks(p):
    log.info(f'Processing {p}...')
    # Read bytes.
    with open(p, 'rb') as fh:
        b = fh.read()
    # Count 24-bit triples.
    counts = collections.Counter()
    values = []
    for i in range(0, len(b) - 3, 3):
        values.append(b[i] | b[i+1]<<8 | b[i+2]<<16)
    _count_blocks(values, counts, 3)
    return counts


def similarity(c1, c2):
    common = sum((c1 & c2).values())
    total = max(sum(c1.values()), sum(c2.values()))
    return common / total


def run(args):
    counts = {p: count_blocks(p) for p in args.path}

    log.info('Computing similarities...')
    maxlen = max(len(p) for p in args.path)
    for p1, p2 in itertools.combinations(counts, 2):
        print(f'{similarity(counts[p1], counts[p2]):<7.2%} | {p1:<{maxlen}} | {p2}')

    log.info('Comparison complete.')
