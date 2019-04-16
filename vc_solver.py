#!/usr/bin/env python

import copy, logging, sys, os, time
from branchbound import branch, branch_and_bound, branch_and_reduce
from vc_preprocessing import *
from igraph import *
from vc_io import *
from crown_decomposition import *
from vc_checker import *

#print (igraph.__version__)

def solve_k_vertex_cover(g, param, v_visited):
    #FILENAME = "samplefile.gr"
    vc_size = param
    solution = set()
    partial = []

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
    # solution = branch_and_bound(g, vc_size, solution)

    # g, k, solution = apply_preprocessing(g, vc_size, solution) # trying out different version with branch and reduce
    # print("after crown reduction preprocesses:")
    # print(g.summary())
    # print("K: " + str(k))
    all_v = [v['original_index'] for v in g.vs]
    # print(g)

    g, k, solution = apply_preprocessing(g, vc_size, solution, v_visited)
    all_v = [v['original_index'] for v in g.vs]
    # print("branching with graph size: " + g.summary())


    rest_solution = branch_and_reduce(g, set(), all_v, k, v_visited)

    rest_solution = [x for x in rest_solution] # input enumerates v from 1
    # solution = [x+1 for x in solution] # input enumerates v from 1
    # print ("found bnb solution: ")
    # print(rest_solution)
    if(len(solution) + len(rest_solution) > vc_size):
        print("not found for k:" + str(vc_size))
        print("size of sol:" + str(len(solution.union(rest_solution))) + " " + str(len(solution) + len(rest_solution)))
    if(len(solution.union(rest_solution)) != len(set(solution) | set(rest_solution))):
        #elements repeat
        print("the same vs taken in preprocessing and branch and reduce")
    return solution.union(rest_solution), v_visited

def bin_search_k_vc(g):
    lower = 0
    upper = g.vcount()
    found = False
    best_solution = [0]*(upper+1)
    v_visited = [0]
    while lower <= upper and not found:
        current = int((upper + lower)/2)
        print("checking for potential vc of size: " + str(current))
        solution, v_visited = solve_k_vertex_cover(copy.deepcopy(graph), current, v_visited)
        if len(solution) == current:
            found = True
            print("found for "+ str(current))
            # print(solution)
        elif len(solution) < current:
            upper = current-1
        else:
            lower = current+1
            print("big")
        if(check_correctness(copy.deepcopy(g), solution) and len(solution) < len(best_solution)):
            best_solution = solution
    return best_solution, v_visited
if __name__ == "__main__":

    logging.basicConfig(filename='performance.log', level=logging.DEBUG)
    logging.info("this is log of perf_counter over each instance.")
    min_k = 1000000
    # for i in range(2830, 2, -1):
    #     print("for k = " + str(i) + "... ")
    #     solution = solve_k_vertex_cover(copy.deepcopy(graph), i)
    #     # print(check_correctness(copy.deepcopy(graph), [x for x in solution]))
    #     print(check_correctness(copy.deepcopy(graph), solution))
    #     if solution != 0 :
    #         # print (solution)
    #         min_k = i
    #     else:
    #         print(min_k)
    #         break
    #     break
    files = [file for file in os.listdir("public") if file.endswith(".gr")]
    for file in sorted(files):
        FILENAME = os.path.join("public", file)
        # FILENAME = "public/vc-exact_001.gr"
        # FILENAME = "degree_two_test.gr"
        print(FILENAME)
        graph = readgraph(FILENAME)
        t = time.perf_counter()
        if(graph.vcount() > 10000):
            continue
        solution, vertices_visited= bin_search_k_vc(copy.deepcopy(graph))
        #measure t elapsed
        elapsed = time.perf_counter() - t
        logging.info("%s took %s to compute", FILENAME, elapsed )
        logging.info("visited " + str(vertices_visited[0]) + " nodes")
        print("checker check:")
        check_correctness(graph, list(solution))
        write_vc(FILENAME[:-3] + "-solution.vc", graph.vcount(), [v for v in solution])
