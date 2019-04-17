#!/usr/bin/env python

import logging
import vc_io, crown_decomposition, branchbound
from igraph import *

def check_correctness(g, vc):
    logging.basicConfig(filename='check.log', level=logging.DEBUG)
    # logging.info("this is log test.")
    g.delete_vertices(vc)
    # print(g)
    print("Nr of edges left: ")
    print(g.ecount())
    if(g.ecount() == 0):
        # logging.info("found cover of size " + str(len(vc)))
        print("found cover of size " + str(len(vc)))
        return True
    return False

def check_cd_correctness():
    G = vc_io.readgraph("example_graph.gr")
    # g, k, sol = crown_decomposition.apply_crown_decomposition(G, 3, set())
    head, partial = crown_decomposition.crown_decomposition(G, 3, set())
    print(head)
    # print(k)
    # print(sol)
    return

def check_maximal_matching():
    G = vc_io.readgraph("example_graph.gr")
    matching = branchbound.get_maximal_matching(G)
    print("checking maximal matching for:")
    print(G)
    print("got matching:")
    print([(G.es[e].target, G.es[e].source) for e in matching])
    return

def check_degree_two_solver():
    G = vc_io.readgraph("degree_two_solver_test.gr")
    sol = branchbound.solve_degree_two(G)
    print(sol)
    return

def draw_solution(g, solution):
    for v in solution:
        g.vs[v]["color"] = "blue"
    plot(g)
