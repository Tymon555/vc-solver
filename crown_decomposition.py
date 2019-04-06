#!/usr/bin/env python

import copy, logging, sys
from igraph import *

def apply_crown_decomposition(G, k, solution):
    #cd graph param has to be passed a copy, not orignial graph
    c = copy.deepcopy(G)
    crown_head, partial = crown_decomposition(c, k, solution)

    if((-1) in partial):
        #k+1 matching -> no-instance
        return G, -1, solution
    if(len(crown_head) == 0):
        # ERROR - guaranteed to be non-empty
        # unless check whether |V| > 3k ???
        print("ERROR IN CD")
    G.delete_vertices(crown_head)
    solution += partial

    print(str(partial) + " taken to solution ")
    k -= len(partial)
    return G, k, solution

#where can I reach using alternating path
def walk(G, v, last_path, Z):
    for n in G.neighbors(v):
        if(G.vs[n]["hk_matched"] != last_path):
            #take to set Z and follow path
            Z.add(G.vs[n])
            walk(G, n, not last_path, Z)
    return

def get_vc_from_matching(G, M, Vm, I):
    #TODO test it
    Z = set()
    for v in Vm:
        if not v["hk_matched"]:
            walk(G, v, True, Z) # unmatched, so no incident edges matching
    #print("Z: " + str(Z))
    S = (Vm-Z) | (I & Z) #Konig's theorem
    #print("S: " + str(S))
    return S

def crown_decomposition(G, k, solution):
    #find maximal (greedy) matching
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
            # #print("deleting ")
            # #print(e)
            G.delete_edges(e)
            # #print(Vm)
            #
    s = set()
    s.update(G.vs)
    I = s-Vm
    #deleting to get bipartite (Vm, I)
    for e in G.es:
        if(G.vs[e.target]["matched"] == True and G.vs[e.source]["matched"] == True):
            G.delete_edges(e)
    for v in G.vs:
        if(v in Vm and G.degree(v) == 0):
            Vm.remove(v)
    #print("found matching of size " + str(matching_size))

    #print("I: " + str(I))
    #print("Vm: " + str(Vm))
    #print(G)
    if(matching_size > k):
        #we are done
        return set(), [-1]
    if matching_size == 0:
        #print("empty matching")
        return set(), []
    ##print(G)
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
            ##print(bfs)
            for i, index in enumerate(bfs[0]):
                parent = bfs[2][index]
                # #print(str(index) + " " + str(parent))
                if(G.vs[index]["hk_matched"] == False and \
                   G.vs[parent]["hk_matched"] == False and \
                   index not in v_in_aug_paths and \
                   parent not in v_in_aug_paths and \
                   index != parent): # is not the same v
                    # #print("found v-disjoint shortest augmented path between " + str(index) + " and "+ str(parent))
                    augmented_paths.add(G.get_eid(index, parent))#found v-disjoint shortest augmented path
                    v_in_aug_paths.add(index)
                    v_in_aug_paths.add(parent)
        if len(augmented_paths) == 0: #empty set
            break
        else :
            M.symmetric_difference_update(augmented_paths)
            augmented_paths.clear()

    #print("M: ")
    #print(str({(G.es[e].source, G.es[e].target) for e in M}))
    vc = get_vc_from_matching(G, M, Vm, I)
    # #print("vs is:")
    # #print (vc)
    # #print("Vm is:")
    # #print(Vm)

    #taking intersection of vc and Vm
    H = vc & Vm
    # #print("crown decomposition with head:")
    # #print(H)
    #print("vc size: "+ str(len(vc)))
    #print("head size: " + str(len(H)))
    #print("graph size: "+ str(G.vcount()))
    #translating into original graph's stuff
    partial = [v["original_index"] for v in H]
    return H, partial
