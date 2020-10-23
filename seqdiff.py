#!/usr/bin/env python

from collections import defaultdict
import sys
import os

# Reference sequence must be first non blank line in file and start with these
# bytes
REF_TAG = "Ref"

# Returns (reference sequence, tag len) where reference sequence is the
# sequence we are comparing mutations to, and tag len is the length of all the
# sequence names in this file
def grab_ref_and_tag_len(l):
    if len(l) < len(REF_TAG) or l[:len(REF_TAG)] != REF_TAG:
        print("Invalid ref line in input file: '{}'".format(l))
        sys.exit(-1)

    # Calculate tag len. Usually 50, sometimes different
    tag_len = len(REF_TAG)
    while tag_len < len(l) and l[tag_len] == " ":
        tag_len += 1

    return grab_seq(l, tag_len), tag_len

def grab_seq(l, tag_len):
    if len(l) < tag_len:
        print("Invalid line in input file: '{}'".format(l))
        sys.exit(-1)
    seq_to_end = l[tag_len:]
    space_offset = seq_to_end.index(" ")
    parsed_seq = seq_to_end[:space_offset]
    parsed_len = int(seq_to_end[space_offset:])
    if len(parsed_seq) != parsed_len:
        print("Got wrong len for seq: {} != {}".format(len(parsed_seq), parsed_len))
        sys.exit(-1)
    return parsed_seq

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: {} <in_0.txt> ... <in_n.txt> <out.csv>".format(sys.argv[0]))
        sys.exit(-1)

    # histograms maps filename -> histogram over mutations in that file
    histograms = {}

    # positions maps integer mutation offset -> set of mutations at that offset
    # (for all files -- since all mutations end up in a single output column)
    positions = defaultdict(set)

    # check no duplicate input filenames
    filenames = sys.argv[1:-1]
    if len(set(filenames)) != len(filenames):
        print("got duplicate input filename")
        sys.exit(-1)

    # reference sequence, filled in by first file and checked against the rest
    master_ref = None

    for fname in filenames:
        # do some simple input filename validation
        if "," in fname or "\n" in fname:
            print("no input file names may contain ',' or '\\n' (got {})".format(fname))
            sys.exit(-1)

        with open(fname) as fin:
            histograms[fname] = defaultdict(int)
            hist = histograms[fname]
            ref = None
            tag_len = None
            for i, l in enumerate(fin):
                # Strip whitespace
                l = l.rstrip()

                # Skip blank lines
                if len(l) == 0:
                    continue

                # Grab reference sequence, ensure the same as previous files if any
                # (ref sequence must be first non-blank line in file)
                if ref is None:
                    ref, tag_len = grab_ref_and_tag_len(l)
                    if master_ref is None:
                        # If this is the first file, remember as master reference
                        master_ref = ref
                        print("got ref: {}".format(ref))
                        print("ref len: {}".format(len(ref)))
                    else:
                        # If this is not the first file, check ref matches
                        if ref != master_ref:
                            print("file {} had different ref than first file: {} != {}".format(fname, ref, master_ref))
                            sys.exit(-1)
                    continue

                # Not a reference line, grab the sequence
                seq = grab_seq(l, tag_len)
                if len(seq) != len(ref):
                    print("line {} had different seq len than ref: {} != {}", i, len(seq), len(ref))
                    sys.exit(-1)

                # Find differences:
                for j, c in enumerate(seq):
                    if c != ".":
                        # Sanity check
                        if c == ref[j]:
                            print("got a non-period at pos {} on line {}, but matched ref seq".format(j, i))
                            sys.exit(-1)

                        # Positions are 1-indexed
                        mut = "{}{}{}".format(ref[j], j + 1, c)

                        # Remember that we have seen a mutation at this position
                        positions[j].add(mut)

                        # Bump the count for this mutation for this file
                        hist[mut] += 1

    # Write out the histograms
    with open(sys.argv[-1], "w") as fout:
        # Write out the csv header
        fout.write("mut,")
        fout.write(",".join(filenames))
        fout.write("\n")

        # For each position (sorted low to high)
        muts = 0
        for p in sorted(positions):
            # For each mutation at a given position that we've seen (sorted alphabetically)
            for mut in sorted(positions[p]):
                # Write out the mutation's name
                fout.write("{}".format(mut))
                for fname in filenames:
                        # Write out how many times that mutation appeared in each file
                        fout.write(",{}".format(histograms[fname][mut]))
                fout.write("\n")
                muts += 1
        print("wrote data for {} mutations across {} files".format(muts, len(filenames)))
