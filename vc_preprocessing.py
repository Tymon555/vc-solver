#!/usr/bin/env python

import crown_decomposition
import sys

def apply_preprocessing(G, k , solution, args, v_visited=[0]):
    #apply all preprocessing rules naively
    old_k = k+1
    if args.optimization >= 2:
        while(old_k != k):
             old_k = k
             G = isolated_v_reduction(G, v_visited)
             G, k, solution= popular_v_reduction(G, k, solution, v_visited)
             if(quad_kernel_reduction(G, k) is False):
                 # print("no-instance")
                 return G, -2, solution
             G, k, solution = pendant_v_reduction(G, k, solution, v_visited)
             G, k, solution = degree_two_reduction(G, k, solution,v_visited )
             # only if other reductions are not doing anything
             if(old_k == k and args.optimization >= 4):
                 G, k, solution = crown_decomposition.apply_crown_decomposition(G, k, solution, v_visited)
    return G, k, solution

def no_param_preprocessing(g, solution):
    size = len(solution ) + 1
    #dummy k to pass to methods originally designed to take parametrized vc
    safe_k = len(g.vs)
    solution = list(solution)
    while(size != len(solution)):
        size = len(solution)
        #w/o parameter still can use pendant and 2-degree rules
        g, _, solution = pendant_v_reduction(g, safe_k, solution)
        g, _, solution = degree_two_reduction(g, safe_k, solution)
    return g, set(solution)
def isolated_v_reduction(G, v_visited):
    degrees = G.degree(G.vs)
    #print(G)
    #deleted = list(range(len(degrees)))
    isolated = []
    #print(deleted)
    v_visited[0] += len(G.vs)
    for i, v in enumerate(degrees):
        if (v == 0):
            isolated.append(G.vs[i])
            #deleted.append(G.vs[i]['original_index'])
            #G.delete_vertices(i)
    #print(G)
    #print(str(isolated))
    # print(str(len(isolated)) + " isolated vertices")
    G.delete_vertices(isolated)
    #print("deleted vs: " + str(deleted))
    return G

def popular_v_reduction (G, k, solution, v_visited):
    degrees = G.degree(G.vs)

    # print("degrees: " + str(degrees))
    popular = []
    partial = []
    v_visited[0] += len(G.vs)
    for i, v in enumerate(degrees):
        if (v > k):
            # print(str(v) + " " + str(k))
            popular.append(G.vs[i])
            partial.append(G.vs[i]['original_index'])
            #k-=1;
    #print(str(popular))
    G.delete_vertices(popular)
    solution |= set(partial)
    k -= len(partial)

    # print(str(len(partial)) + " popular vertices")
    # print("deleted vs: " + str(deleted))
    return G, k, solution

def pendant_v_reduction(G, k, solution, v_visited):
    degrees = G.degree(G.vs)

    pendant = []
    neighbrs = []
    partial = []

    v_visited[0] += len(G.vs)
    for i, d in enumerate(degrees):
        # print(str(i) + " " + str(d))
        if( d == 1 ):
            adj = G.neighbors(G.vs[i])
            adj = adj[0]
            if(G.vs[i]['original_index'] not in partial):
                #to not add two adjacent pendant vs
                # print(":add")
                pendant.append(G.vs[i])
                neighbrs.append(adj)
                partial.append(G.vs[adj]['original_index'])

    # print("pendant: " + str(pendant))
    G.delete_vertices(neighbrs+pendant)
    solution |= set(partial)
    k -= len(partial)
    # if(partial):
        # print(str(len(partial)) + " pendant vertices")
    
    return G, k, solution

def degree_two_reduction(G, k, solution, v_visited):
    degrees = G.degree(G.vs)

    taken = []
    partial = []

    v_visited[0] += len(G.vs)
    for i, d in enumerate(degrees):
        if( d == 2 ):
            #print("degree2")
            adj = G.neighbors(G.vs[i])
            if(G.get_eid(adj[0], adj[1], True, False) != -1):
                #take both neighbors
                if(adj[0] not in taken and adj[1] not in taken):
                    taken.append(adj[0])
                    taken.append(adj[1])
                    partial.append(G.vs[adj[0]]['original_index'])
                    partial.append(G.vs[adj[1]]['original_index'])
            # else:
                #VC.6. merge three vs into two
                #TODO: find a way to remember the solution
                # n = G.neighborhood([G.vs[i], adj[0], adj[1]])
                # neighbrd = list(set().union(n[0], n[1], n[2]))
                # neighbrd.remove(i)
                # neighbrd.remove(adj[1])
                # neighbrd.remove(adj[0])
                # #remove and replace with single vertex; decrease k
                # G.delete_vertices(adj.append(i))
                # print("union of neighborhoods: " + str(neighbrd))


    # print("added to vc: " + str(taken))
    G.delete_vertices(taken)
    solution |= set(partial)
    k -= len(partial)
    return G, k, solution

def quad_kernel_reduction(G, k):
    #use AFTER removing isolated and popular vertices
    #then if |V|+|E| > 3k^2 we have no-instance
    V = G.vcount()
    E = G.ecount()
    if(V > k*k+k or E > k*k):
        return False
    else:
        return True
