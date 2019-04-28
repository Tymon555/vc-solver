#!/usr/bin/env python

import copy, logging, sys, os, time, argparse, signal
from branchbound import branch, branch_and_bound, branch_and_reduce, get_maximal_matching
from vc_preprocessing import *
from igraph import *
from vc_io import *
from crown_decomposition import *
from vc_checker import *
from graph_generator import *
#print (igraph.__version__)

class TimeoutException(Exception):
    pass

def timeout_handler(signum, frame):
    if(args.verbose >= 3):
        print("\ntime limit exceeded\n")
    raise TimeoutException("tle")

def solve_k_vertex_cover(g, param, v_visited, args):
    #FILENAME = "samplefile.gr"
    vc_size = param
    solution = set()
    partial = []

        #if(args.verbose >= 3):
# print(v.attributes())
    # old_k = vc_size+1
    # while(True):
    #     if(vc_size < 0):
    #         print "-1"
    #         break
    #     if(vc_size == 0):
    #         #if(args.verbose >= 3):
# print(g)
    #         if(ecount == 0):
    #             print solution
    #             break
    #         else:
    #             print "-1"
    #             break

    #     if(ecount == 0):
    #         #if(args.verbose >= 3):
# print(g)
    #         print solution
    #         while(old_k != vc_size):
    #             old_k = vc_size
    #             g = isolated_v_reduction(g)
    #             g, vc_size, solution= popular_v_reduction(g, vc_size, solution)
    #             if(quad_kernel_reduction(g, vc_size) is False):
    #                 if(args.verbose >= 3):
# print("no-instance")
    #                 sys.exit(0)
    #             g, vc_size, solution = pendant_v_reduction(g, vc_size, solution)
    #             g, vc_size, solution = degree_two_return eduction(g, vc_size, solution)

    #             g, vc_size, solution = apply_crown_decomposition(g, vc_size, solution)
    #             # if(args.verbose >= 3):
# print(crown_head[:20])


    if(args.verbose >= 3):
        print("after reductions:")
    if(args.verbose >= 3):
        print(g.summary() + "\nk: " + str(vc_size))
    # solution = branch_and_bound(g, vc_size, solution)

    # g, k, solution = apply_preprocessing(g, vc_size, solution) # trying out different version with branch and reduce
    if(args.verbose >= 3):
        print("after crown reduction preprocesses:")
    if(args.verbose >= 3):
        print(g.summary())
    # if(args.verbose >= 3):
    #     print("K: " + str(k))

    g, k, solution = apply_preprocessing(g, vc_size, solution, args, v_visited)
    all_v = [v['original_index'] for v in g.vs]
    if(args.verbose >= 3):
        print("branching with graph size: " + g.summary())


    rest_solution = branch_and_reduce(g, set(), all_v, k, args, v_visited)

    rest_solution = [x for x in rest_solution] # input enumerates v from 1
    # solution = [x+1 for x in solution] # input enumerates v from 1
    # print ("found bnb solution: ")
    if(args.verbose >= 3):
        print(rest_solution)
    if(len(solution) + len(rest_solution) > vc_size):
        # if(args.verbose >= 3):
# print(solution)
        if(args.verbose >= 3):
            print(rest_solution)
        if(args.verbose >= 3):
            print("not found for k:" + str(vc_size))
        if(args.verbose >= 3):
            print("size of sol:" + (len(solution.union(rest_solution))) + " " + str(len(solution) + len(rest_solution)))
    if(len(solution.union(rest_solution)) != len(set(solution) | set(rest_solution))):
        #elements repeat
        if(args.verbose >= 3):
            print("the same vs taken in preprocessing and branch and reduce")
    return solution.union(rest_solution), v_visited

# def linear_search_k_vc(g):
#     k = 0
#     v_visited = [0]
#     found = False
#     k=0
#     while not found:
#         solution = solve_k_vertex_cover(Graph.copy(g), k, args, v_visited)
#         if(check_correctness(Graph.copy(g), solution)):
#             found = True
#             k += 1
#     return solution
def bin_search_k_vc(g, args):
    for v in g.vs:
        v['original_index'] = v.index
        v['name'] = str(v.index)
    v_visited = [0]
    # print("assigned name and org index")
    reduced_g, _, partial = apply_preprocessing(Graph.copy(g), g.vcount(), set(), args, v_visited)
    if(args.verbose >= 3):
        print("initial preprocessing done:")
    if(args.verbose >= 3):
        print(summary(reduced_g))
    lower = len(branchbound.get_maximal_matching(reduced_g, v_visited)[0])
        # for manual choice of how big is too big
        # if(lower > 1000):
        #     return lower, v_visited
    upper = reduced_g.vcount()
    found = False
    best_solution = [0]*(upper+1)
    if(args.verbose >= 3):
        print("starting binary search...")
    if(args.verbose >= 3):
        print("lower bound: "+ len(lower))
    while lower <= upper and not found:
        current = int((upper + lower)/2)
        if(args.verbose >= 3):
            print("checking for potential vc of size: " + str(current))
        solution, v_visited = solve_k_vertex_cover(Graph.copy(reduced_g), current, v_visited, args)
        if len(solution) == current:
            found = True
            if(args.verbose >= 3):
                print("found for "+ str(current))
                # if(args.verbose >= 3):
                print(solution)
        elif len(solution) < current:
            upper = current-1
            #can do that (assumed to large k)
            found = True
            if(args.verbose >= 3):
                print("found for "+ str(current))
        else:
            lower = current+1
        if(len(solution) < len(best_solution)):
            best_solution = solution

    best_solution = {int(v) for v in best_solution}
    if(args.verbose >= 3):
        print(best_solution)
    # while True:
    #     current -= 1
    #     if(args.verbose >= 3):
    # print("checking for smaller k: "+ str(current))
    #     solution, v_visited = solve_k_vertex_cover(reduced_g.copy(), current, v_visited, args)
    #     if(check_correctness(reduced_g.copy(), solution) and len(solution) < len(best_solution)):
    #         if(args.verbose >= 3):
    # print("foudn better")
    #         best_solution = solution
    #     else:
    #         break

    best_solution |= partial
    if(args.verbose >= 3):
        print(best_solution)

    return best_solution, v_visited
if __name__ == "__main__":
    # for logging performance of the program
    logging.basicConfig(filename='performance_measure.log', level=logging.DEBUG)
    logging.info("\nthis is log of perf_counter over each instance.")
    # min_k = 1000000

    # for command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--optimization", type=int, choices=[0,1,2,3,4,5], help="choose \
                        optimization level: 0 - none, 1 - add upper and lower bound; 2 - \
                        add quadratic kernel, 3 - add interleaving, 4 - add linear kernel, \
                        5 - use local preprocessing rules (bfs from neighborhood of deleted v)",\
                        default = 5)
    parser.add_argument("-d", "--draw", help = "draws solution using PyCairo library", action="store_true")
    parser.add_argument("-t", "--timeout", help="# of seconds before a single instace raises \
                        an Exception", type = int, default = 10)
    parser.add_argument("folder", help="path to problem instances")
    parser.add_argument("-v", "--verbose", help="debug to stdout", type=int, choices=[0,1,2,3], \
                        default=0)
    args = parser.parse_args()
    #so we dont get tle on drawing modules
    if(args.draw):
        args.timeout = 10000
    logging.info(str("optimization level: " + str(args.optimization)))
    if(args.verbose >= 3):
        print("timeout: "+ str(args.timeout))
    # for timeout on too large instances:
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(args.timeout)

    # for i in range(2830, 2, -1):
    #     if(args.verbose >= 3):
# print("for k = " + str(i) + "... ")
    #     solution = solve_k_vertex_cover(graph.copy(), i)
    #     # if(args.verbose >= 3):
# print(check_correctness(graph.copy(), [x for x in solution]))
    #     if(args.verbose >= 3):
# print(check_correctness(graph.copy(), solution))
    #     if solution != 0 :
    #         # print (solution)
    #         min_k = i
    #     else:
    #         if(args.verbose >= 3):
# print(min_k)
    #         break
    #     break
    # folder = "public"
    # if(len(sys.argv) > 1):
    #     folder = sys.argv[1]
    folder = args.folder
    if folder == "generate":
        graphs = generate_ER_graphs()
        for i, graph in enumerate(graphs):
            t = time.perf_counter()
            # if(graph.vcount() > 10000):
            #     continue
            solution, vertices_visited= bin_search_k_vc(graph, args)
            # solution, vertices_visited = linear_search_k_vc(graph.copy())
            #measure t elapsed
            elapsed = time.perf_counter() - t
            FILENAME = "todo"
            logging.info("%s took %self to compute", FILENAME, elapsed )
            logging.info("visited " + str(vertices_visited[0]) + " nodes")
            if(args.verbose >= 3):
                print("checker check:")
            draw_solution(graph, solution)
            check_correctness(graph, list(solution))

    files = [file for file in os.listdir(folder) if file.endswith(".gr") or file.endswith(".edge")]

    for file in sorted(files):
        FILENAME = os.path.join(folder, file)
        # FILENAME = "public/vc-exact_001.gr"
        # FILENAME = "degree_two_test.gr"
        if(args.verbose >= 1):
            print(FILENAME)
        graph = readgraph(FILENAME)
        t = time.perf_counter()
        # if(graph.vcount() > 10000):
        #     continue
        try:
            solution, vertices_visited= bin_search_k_vc(Graph.copy(graph), args)
        except TimeoutException as exc:
            print(exc)
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(args.timeout)
            logging.info("%s %s TIMEOUT", FILENAME, graph.vcount())
            if(args.verbose >= 3):
                print("timeout")
            continue
        if type(solution) == int:
            if(args.verbose >= 3):
                print("vc to calculate is to big (lower bound " + str(solution) + ")")
            continue
        # solution, vertices_visited = linear_search_k_vc(graph.copy())
        #measure t elapsed
        elapsed = time.perf_counter() - t
        # logging.info("%s took %s to compute", FILENAME, elapsed )
        # logging.info("%s %s", FILENAME, elapsed )
        # logging.info("visited " + str(vertices_visited[0]) + " nodes")
        logging.info("%s %s %s %s %s", FILENAME, graph.vcount(), elapsed, vertices_visited[0], len(solution))
        if(args.verbose >= 3):
            print("checker check:")
        check_correctness(Graph.copy(graph), list(solution))
        if(args.draw):
            draw_solution(graph, solution)
        write_vc(FILENAME[:-3] + "-solution.vc", graph.vcount(), [v for v in solution])
