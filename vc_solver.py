#!/usr/bin/env python

import copy, logging, sys
from branchbound import branch
from vc_preprocessing import *
from igraph import *
from vc_io import *
from crown_decomposition import *

#print (igraph.__version__)

def solve_k_vertex_cover(g, param):
    logging.basicConfig(filename='example.log', level=logging.DEBUG)
    logging.info("this is log test.")
    #FILENAME = "samplefile.gr"
    # FILENAME = "degree_two_test.gr"
    vc_size = param
    solution = []
    partial = []

    # g.add_vertices(8)
    # g.add_edges([(1,2), (2,3), (2,4), (4,5), (4,1)])

    for v in g.vs:
        v['original_index'] = v.index
        #print(v.attributes())
    # old_k = vc_size+1
    # while(True):
    #     if(vc_size < 0):
    #         print "-1"
    #         break
    #     if(vc_size == 0):
    #         #print(g)
    #         if(ecount == 0):
    #             print solution
    #             break
    #         else:
    #             print "-1"
    #             break

    #     if(ecount == 0):
    #         #print(g)
    #         print solution
    #         while(old_k != vc_size):
    #             old_k = vc_size
    #             g = isolated_v_reduction(g)
    #             g, vc_size, solution= popular_v_reduction(g, vc_size, solution)
    #             if(quad_kernel_reduction(g, vc_size) is False):
    #                 print("no-instance")
    #                 sys.exit(0)
    #             g, vc_size, solution = pendant_v_reduction(g, vc_size, solution)
    #             g, vc_size, solution = degree_two_return eduction(g, vc_size, solution)

    #             g, vc_size, solution = apply_crown_decomposition(g, vc_size, solution)
    #             # print(crown_head[:20])


    # print("after reductions:")
    # print(g.summary() + "\nk: " + str(vc_size))
    solution = branch(g, vc_size, solution)
    if solution != 0:
        solution = [x+1 for x in solution] # input enumerates v from 1
    return(solution)

if __name__ == "__main__":

    FILENAME = "public/vc-exact_001.gr"
    graph = readgraph(FILENAME)
    min_k = 1000000
    for i in range(2996, 2900, -1):
        print("for k = " + str(i) + "... ")
        solution = solve_k_vertex_cover(copy.deepcopy(graph), i)
        if solution != 0 :
            print (solution)
            min_k = i
        else:
            print(min_k)
            break
