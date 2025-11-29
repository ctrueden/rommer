import collections
import functools
import itertools
import logging

log = logging.getLogger(__name__)

# TODO - check out these projects of interest:
# - https://github.com/mendsley/bsdiff
# - https://radareorg.github.io/blog/posts/binary-diffing/

blurb = "compute similarity of binary files"
description = """Compare files for matching byte sequences.

The command prints a similarity percentage between every pair of input files.

Each byte-triple is interpreted as an integer value in range(0, 2**24):

    ABC, BCD, CDE, DEF, EFG, FGH, GHI, HIJ, IJK, JKL, etc.

These values are counted, then hashed with their adjacent triple:

    ABC, BCD, CDE, DEF, EFG, FGH, GHI, etc.
    ^^^            ^^^
     \\--------------/
            |
           A-F, B-G, C-H, D-I, E-J, F-K, G-L, etc.

These combined 24-bit values are then counted and merged again:

           A-F, B-G, C-H, D-I, E-J, F-K, G-L, etc.
           ^^^                           ^^^
            \\-----------------------------/
                           |
                          A-L, B-M, C-N, etc.

And so on until each hashed value spans more than 50% of the file,
at which point the process cannot continue.
"""


def configure(parser):
    parser.add_argument("path", nargs="+", help="file path to compare")


def _combine(x, y):
    # TODO: Improve combine function. Result must be in [0, 2**24).
    return x ^ y
    # return (0xaaa & (x ^ 0xfa7)) | (0x555 & (y ^ 0xc4b))


def _count_blocks(values, counts, spread):
    # TODO: Count higher-spread aggregate values with more weight.
    # The question is: how much more?
    counts.update(values)
    if len(values) <= spread:
        # Hash what's left together, to help avoid false 100% reports.
        fv = [functools.reduce(_combine, values)]
        print(fv)
        counts.update(fv)
        return

    # Merge adjacent values and recurse
    nv = []
    for i in range(len(values) - spread):
        nv.append(_combine(values[i], values[i + spread]))
    _count_blocks(nv, counts, spread * 2)


def count_blocks(p):
    log.info(f"Processing {p}...")
    # Read bytes.
    with open(p, "rb") as fh:
        b = fh.read()
    # Count 24-bit triples.
    counts = collections.Counter()
    values = []
    for i in range(0, len(b) - 3, 3):
        values.append(b[i] | b[i + 1] << 8 | b[i + 2] << 16)
    _count_blocks(values, counts, 3)
    return counts


def similarity(c1, c2):
    common = sum((c1 & c2).values())
    total = max(sum(c1.values()), sum(c2.values()))
    return common / total


def run(args):
    counts = {p: count_blocks(p) for p in args.path}

    log.info("Computing similarities...")
    maxlen = max(len(p) for p in args.path)
    for p1, p2 in itertools.combinations(counts, 2):
        print(f"{similarity(counts[p1], counts[p2]):<7.2%} | {p1:<{maxlen}} | {p2}")

    log.info("Comparison complete.")
