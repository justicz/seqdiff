#!/usr/bin/env python3

from collections import defaultdict
import sys

# Sequences start at byte 50 and run until a space
SEQ_OFFSET = 50

def grab_ref(l):
    if len(l) < 3 or l[:3] != "Ref":
        print("Invalid ref line in input file: '{}'".format(l))
        sys.exit(-1)
    return grab_seq(l)

def grab_seq(l):
    if len(l) < SEQ_OFFSET:
        print("Invalid line in input file: '{}'".format(l))
        sys.exit(-1)
    seq_to_end = l[SEQ_OFFSET:]
    space_offset = seq_to_end.index(" ")
    parsed_seq = seq_to_end[:space_offset]
    parsed_len = int(seq_to_end[space_offset:])
    if len(parsed_seq) != parsed_len:
        print("Got wrong len for seq: {} != {}".format(len(parsed_seq), parsed_len))
        sys.exit(-1)
    return parsed_seq

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: {} <in> <out>".format(sys.argv[0]))
        sys.exit(-1)

    hist = {}
    order = defaultdict(list)
    with open(sys.argv[1]) as fin:
        found_ref = False
        ref = ""
        for i, l in enumerate(fin):
            # Strip whitespace
            l = l.rstrip()

            # Skip blank lines
            if len(l) == 0:
                continue

            # Fill in reference map
            if not found_ref:
                ref = grab_ref(l)
                print("got ref: {}".format(ref))
                print("ref len: {}".format(len(ref)))
                found_ref = True
                continue

            # Not a reference line, grab the sequence
            seq = grab_seq(l)
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
                    key = "{}{}{}".format(ref[j], j + 1, c)

                    # If we haven't seen a key before, allocate a count, and
                    # remember what order we saw it in
                    if hist.get(key, None) is None:
                        hist[key] = 1
                        order[j].append(key)
                    else:
                        # Otherwise just bump the count
                        hist[key] += 1

    # Write out the histogram
    with open(sys.argv[2], "w") as fout:
        for j in sorted(order):
            for k in order[j]:
                fout.write("{},{}\n".format(k, hist[k]))
        print("wrote {} lines".format(len(order)))
