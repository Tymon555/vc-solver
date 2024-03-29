#!/usr/bin/env python

import copy, logging, sys
from queue import *
from igraph import *

def apply_crown_decomposition(G, k, solution, v_visited):
    #cd graph param has to be passed a copy, not orignial graph
    # c = copy.deepcopy(G)
    # crown decomp only guaranteed if |v| > 3k
    if(G.vcount() <= 3*k):
        #print("already have a kernel")
        # #print(c.vcount())
        # #print(3*k)
        return G, k, solution
    crown_head, partial = crown_decomposition(G, k, solution, v_visited)

    if((-1) in partial):
        #k+1 matching -> no-instance
        return G, -1, solution
    if(len(crown_head) == 0):
        raise RuntimeError("empty crown head")
        # ERROR - guarantGraph.copyeed to be non-empty
        # unless check whether |V| > 3k ???
        #print("ERROR IN CD")
    G.delete_vertices(crown_head)
    solution |= set(partial)

    print(str(partial) + " taken to solution ")
    #print("crown reduction found partial of size " + str(len(partial)))
    k -= len(partial)
    # #print(k)
    return G, k, solution

#where can I reach using alternating path
def walk(G, v, last_path, Z, v_visited):
    for n in G.neighbors(v):
        v_visited[0] += 1
        if(G.vs[n]["hk_matched"] != last_path):
            #take to set Z and follow path
            Z.add(G.vs[n])
            walk(G, n, not last_path, Z, v_visited)
    return

def get_vc_from_matching(G, M, Vm, I, v_visited):
    #TODO test it
    Z = set()
    # v_visited[0] += 1
    for v in Vm:
        if not v["hk_matched"]:
            walk(G, v, True, Z, v_visited) # unmatched, so no incident edges matching
    ##print("Z: " + str(Z))
    S = (Vm-Z) | (I & Z) #Konig's theorem
    # #print("S: " + str(S))
    return S

def crown_decomposition(G, k, solution, v_visited=[0], debug = False):
    if debug:
        org = G.copy()
        plot(org, vertex_label = [v.index for v in org.vs])
    G = G.copy()
    # requirement for crown reduction
    # if(G.vcount() > 3*k):
    #     #print("g has more than 3k vertices")
    #     return set(), []
    #find maximal (greedy) matching
    matching_size = 0
    Vm = set()
    v_visited[0] += len(G.vs)
    for v in G.vs:
        v["matched"] = False
    to_delete = []
    for i, e in enumerate(G.es):
        # #print("for "+ str(e))
        v_visited[0] += 2
        if(G.vs[e.target]["matched"] == False and G.vs[e.source]["matched"] == False  ):
            G.vs[e.target]["matched"] = True
            G.vs[e.source]["matched"] = True
            matching_size += 1
            Vm.add(G.vs[e.target])
            Vm.add(G.vs[e.source])
            # #print("deleting ")
            # #print(e)
            # #print(G.vs[e.target])
            # #print(G.vs[e.source])
            to_delete.append(e)
            # #print(Vm)
            #
    #print([(G.vs[e.source], G.vs[e.target]) for e in to_delete])
    G.delete_edges(to_delete)
    s = set()
    s.update(G.vs)
    I = s-Vm
    #deleting to get bipartite (Vm, I)
    # #print(G.ecount())
    to_delete = []
    for i, e in enumerate(G.es):
        v_visited[0] += 2
        # #print( str(e.target) + " " + str(e.source))
        if(G.vs[e.target]["matched"] == True and G.vs[e.source]["matched"] == True):
            # #print("to bipratite" + str(e.target) + " " + str(e.source))
            to_delete.append(e)
    G.delete_edges(to_delete)
    org.delete_edges(to_delete)
    v_visited[0] += len(G.vs)
    for v in G.vs:
        if(v in Vm and G.degree(v) == 0):
            Vm.remove(v)
    # #print("found matching of size " + str(matching_size))
    # #print()
    # print("I: " + str(I))
    # print("Vm: " + str(Vm))
    # print(G)
    if(matching_size > k):
        #we are done
        return set(), [-1]
    if matching_size == 0:
        ##print("empty matching")
        return set(), []
    ###print(G)
    #hopcroft-karp for maximum matching
    #and minimum v-c for G_i,v bipartite graph
    # G.vs[x]["matched"]: True->V_m, False - I
    M = set() # our maximum matching
    v_visited[0] += len(G.vs)
    for v in G.vs:
        v["hk_matched"] = False # those

    augmented_paths = set()
    v_in_aug_paths = set()
    # while True:
    #     for v in Vm:
    #         if v["hk_matched"] == True :
    #             continue
    #         bfs = G.bfs(v.index)
    #         #print(bfs)
    #         for i, index in enumerate(bfs[0]):
    #             parent = bfs[2][index]
    #             #print(str(index) + " " + str(parent))
    #             if(G.vs[index]["hk_matched"] == False and \
    #                G.vs[parent]["hk_matched"] == False and \
    #                index not in v_in_aug_paths and \
    #                parent not in v_in_aug_paths and \
    #                index != parent): # is not the same v
    #                 # ##print("found v-disjoint shortest augmented path between " + str(index) + " and "+ str(parent))
    #                 augmented_paths.add(G.get_eid(index, parent))#found v-disjoint shortest augmented path
    #                 v_in_aug_paths.add(index)
    #                 v_in_aug_paths.add(parent)

    #     if len(augmented_paths) == 0: #empty set
    #         break
    #     else :
    #         M.symmetric_difference_update(augmented_paths)
    #         augmented_paths.clear()
    q = Queue()
    for v in Vm:
        v_visited[0] += 1
        q.put(v.index)
    while True:
        G, augmented_paths, v_in_aug_paths = hk_bfs(G, q, v_in_aug_paths, v_visited)
        if not augmented_paths:
            break
        else:
            M.symmetric_difference_update(augmented_paths)
            augmented_paths.clear()
    # #print("M: ")
    # #print(str({(G.es[e].source, G.es[e].target) for e in M}))
    # for e in M:
    #     G.es[e]['color']='blue'
    # plot(G)
    vc = get_vc_from_matching(G, M, Vm, I, v_visited)
    # ##print("vs is:")
    # #print (vc)
    # ##print("Vm is:")
    # ##print(Vm)

    #taking intersection of vc and Vm
    H = vc & Vm
    partial = [v["original_index"] for v in H]
    if debug:
        k = org.neighborhood(partial)
        k = [item for sublist in k for item in sublist]
        print(k)
        C = set(k) - set(partial)
        R = set(org.vs)- {org.vs[e] for e in (set(partial)|C)}
        print(R)
        for i in C:
            org.vs[i]['color'] = 'pink'
        for v in partial:
            org.vs[v]['color'] = 'blue'
        for v in R:
            v['color'] = 'yellow'

        plot(org, vertex_label = [v.index for v in org.vs])
    # ##print("crown decomposition with head:")
    # ##print(H)
    ##print("vc size: "+ str(len(vc)))
    ##print("head size: " + str(len(H)))
    ##print("graph size: "+ str(G.vcount()))
    #translating into original graph's stuff
    return H, partial

def hk_bfs(G, vs, v_in_aug_paths, v_visited):
    v_visited[0] += G.vcount()
    layer = 0
    for v in G.vs:
        v["used"] = False
    while True:
        augmented_paths = set()
        v_in_aug_paths = set()
        layer += 1
        side = list(vs.queue)
        for v in side:
            if G.vs[v]["hk_matched"] == False:
                augmented_paths = hk_dfs(G, v, augmented_paths, v_in_aug_paths, v_visited, False)
        if not augmented_paths:
            break
    # while(not vs.empty()):
    #     v = vs.get()
    #     v_visited[0] += 1
    #     ns = G.neighbors(v)
    #     # #print(v)
    #     # #print(ns)
    #     v_visited[0] += len(ns)
    #     for n in ns:
    #         if(G.vs[v]["hk_matched"] == False and \
    #            G.vs[n]["hk_matched"] == False and \
    #            v not in v_in_aug_paths and \
    #            n not in v_in_aug_paths):
    #             augmented_paths.add(G.get_eid(v, n))
    #             G.vs[v]["hk_matched"] = True
    #             G.vs[n]["hk_matched"] = True
    #             # #print(G.vs[n]["hk_matched"])
    #             v_in_aug_paths.add(v)
    #             v_in_aug_paths.add(n)

    return G, augmented_paths, v_in_aug_paths

def hk_dfs(G, v,augmented_paths, v_in_aug_paths, v_visited, coveredFlag, path=set()):
    v_visited[0] += 1
    ns = G.neighbors(v)
    for n in ns:
        if(not G.vs[n]["used"] and \
            G.get_eid(v, n) in augmented_paths == coveredFlag):
            path.add(G.get_eid(v, n))
            # if found aug path...
            if not G.vs[n]["hk_matched"] :
               augmented_paths.update()
               G.vs[v]["hk_matched"] = True
               G.vs[n]["hk_matched"] = True
            else :
                augmented_paths = hk_dfs(G, n, augmented_paths, v_in_aug_paths, v_visited, not coveredFlag, path)
    return augmented_paths
