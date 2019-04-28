#!/usr/bin/env python

import pstats, io, os
# save most time-consuming functions from profiler output to a text file
def main(filename='solver_profile'):
    with open(filename, "r") as f:
        with open("solver_stats", "w+") as w:
            s = io.StringIO()
            p = pstats.Stats(filename, stream = s)
            p.strip_dirs().sort_stats('tottime').print_stats(20)
            w.write(s.getvalue())

def get_sol_sizes(folder):

    files = [file for file in os.listdir(folder) if file.endswith(".vc")]
    for file in sorted(files):
        fn = os.path.join(folder, file)
        with open(fn, "r") as f:
            l = f.readline().split()
            print(str(file) + " " + str(l[3]))
if __name__ == "__main__":
    main()
