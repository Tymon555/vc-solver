#!/usr/bin/env python

import copy, logging, sys
from branchbound import branch_and_bound
from vc_preprocessing import *
from igraph import *
from vc_io import *
from crown_decomposition import *

#print (igraph.__version__)
if __name__ == "__main__":
    logging.basicConfig(filename='example.log', level=logging.DEBUG)
    logging.info("this is log test.")
    #FILENAME = "samplefile.gr"
    FILENAME = "degree_two_test.gr"
    FILENAME = "public/vc-exact_001.gr"
    g = readgraph(FILENAME)
    vc_size = 2571
    solution = []
    partial = []

    # g.add_vertices(8)
    # g.add_edges([(1,2), (2,3), (2,4), (4,5), (4,1)])

    for v in g.vs:
        v['original_index'] = v.index
        #print(v.attributes())
    old_k = vc_size+1
    while(old_k != vc_size):
        old_k = vc_size
        g = isolated_v_reduction(g)
        g, vc_size, solution= popular_v_reduction(g, vc_size, solution)
        if(quad_kernel_reduction(g, vc_size) is False):
            print("no-instance")
            sys.exit(0)
        g, vc_size, solution = pendant_v_reduction(g, vc_size, solution)
        g, vc_size, solution = degree_two_reduction(g, vc_size, solution)

    print("after reductions:")
    print(g.summary() + "\nk: " + str(vc_size))
    solution = branch_and_bound(g, vc_size, solution)
    solution = [x+1 for x in solution] # input enumerates v from 1
    print(solution)
