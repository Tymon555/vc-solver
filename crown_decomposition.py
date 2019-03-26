#!/usr/bin/env python

import copy, logging, sys
from vc_preprocessing import *
from igraph import *

#where can I reach using alternating path
def walk(G, v, last_path, Z):
    for n in G.neighbors(v):
        if(G.vs[n]["hk_matched"] != last_path):
            #take to set Z and follow path
            Z.add(n)
            walk(G, n, not last_path, Z)
    return

def get_vc_from_matching(G, M, Vm, I):
    #TODO test it
    Z = set()
    for v in Vm:
        if not v["hk_matched"]:
            walk(G, v, True, Z) # unmatched, so no incident edges matching
    S = (Vm-Z) | (I & Z) #Konig's theorem

    return S

def crown_decomposition(G, k, solution):
    #find matching
    matching_size = 0
    Vm = set()
    for v in G.vs:
        v["matched"] = False
    for e in G.es:
        if(G.vs[e.target]["matched"] == False and G.vs[e.source]["matched"] == False  ):
            G.vs[e.target]["matched"] = True
            G.vs[e.source]["matched"] = True
            matching_size += 1
            Vm.add(G.vs[e.target])
            Vm.add(G.vs[e.source])
            print("deleting ")
            print(e)
            G.delete_edges(e)
            # print(Vm)
    print("found matching of size " + str(matching_size))
    s = set()
    s.update(G.vs)
    I = s-Vm

    if(matching_size > k):
        #we are done
        return False

    print(G)
    #hopcroft-karp for maximum matching
    #and minimum v-c for G_i,v bipartite graph
    # G.vs[x]["matched"]: True->V_m, False - I
    M = set() # our maximum matching
    for v in G.vs:
        v["hk_matched"] = False # those


    augmented_paths = set()
    v_in_aug_paths = set()
    while True:
        for v in Vm:
            if v["hk_matched"] == True :
                continue
            bfs = G.bfs(v.index)
            #print(bfs)
            for i, index in enumerate(bfs[0]):
                parent = bfs[2][index]
                # print(str(index) + " " + str(parent))
                if(G.vs[index]["hk_matched"] == False and \
                   G.vs[parent]["hk_matched"] == False and \
                   index not in v_in_aug_paths and \
                   parent not in v_in_aug_paths and \
                   index != parent): # is not the same v
                    # print("found v-disjoint shortest augmented path between " + str(index) + " and "+ str(parent))
                    augmented_paths.add(G.get_eid(index, parent))#found v-disjoint shortest augmented path
                    v_in_aug_paths.add(index)
                    v_in_aug_paths.add(parent)
        if len(augmented_paths) == 0: #empty set
            break
        else :
            M.symmetric_difference_update(augmented_paths)
            augmented_paths.clear()

    vc = get_vc_from_matching(G, M, Vm, I)
    # print("vs is:")
    # print (vc)
    # print("Vm is:")
    # print(Vm)

    #taking intersection of vc and Vm
    H = vc & Vm
    # print("crown decomposition with head:")
    # print(H)
    print("head size: " + str(len(H)))
    #translating into original graph's stuff
    ret = [v["original_index"] for v in H]
    return ret
