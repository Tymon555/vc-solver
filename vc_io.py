#!/usr/bin/env python

import logging
from igraph import *
def readgraph(filename):

    logging.basicConfig(filename='example.log', level=logging.DEBUG)
    G = Graph()
    edges = []
    with open(filename) as f:
        content = f.readlines()
    #print (content)
    for line in content:
        line.strip()
        if(line[0] == 'c'):
            continue
        if(line[0] == 'p'):
            line = line.split()
            vcount = int(line[2])
            ecount = int(line[3])
            print("Starting with " + line[2] + " vertices and " + line[3] + " edges.")
            G.add_vertices(vcount)
        if(line[0].isdigit()):
            line = line.split()
            edges.append((int(line[0])-1, int(line[1])-1))
    #print(str(edges))

    if(len(edges) != ecount):
        print("ecount different to # of edges read.")

    #print(G)
    G.add_edges(edges)

    return G


def write_vc(filename, graph_size, vc):
    with open(filename, "w+") as f:
        f.write("s vc " + str(graph_size) + " " + str(len(vc)) + "\n")
        for v in vc:
            f.write(str(v) + "\n")
    return
