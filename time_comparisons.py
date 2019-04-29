#!/usr/bin/env python

import igraph
import timeit
def find(g):
    g.vs.find("9999")


def main():
    g = igraph.Graph.GRG(10000, 0.1)
    # print(g)
    for v in g.vs:
        v['name'] = str(v.index)
    print(g.vs[9999]['name'])
    print(igraph.summary(g))
    # timeit.timeit(g.vs.find(name="9999"))
    timeit.repeat("find(g)", "from __main__ import find, g")
if __name__ == "__main__":
    main()
