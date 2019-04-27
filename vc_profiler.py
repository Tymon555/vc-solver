#!/usr/bin/env python

import pstats, io
# save most time-consuming functions from profiler output to a text file
def main(filename='solver_profile'):
    with open(filename, "r") as f:
        with open("solver_stats", "w+") as w:
            s = io.StringIO()
            p = pstats.Stats(filename, stream = s)
            p.strip_dirs().sort_stats('tottime').print_stats(20)
            w.write(s.getvalue())
if __name__ == "__main__":
    main()
