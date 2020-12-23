import collections
import itertools
import logging
import rommer
import time

log = logging.getLogger(__name__)

blurb = 'compute similarity of binary files'
description = '''Compare files for identical byte sequences.

Each file is indexed in blocks
'''


def configure(parser):
    parser.add_argument('path', nargs='+', help='file path to scan')


def _count_blocks(values, counts, spread):
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
