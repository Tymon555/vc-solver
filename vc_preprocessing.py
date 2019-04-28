#!/usr/bin/env python

import crown_decomposition
import sys, queue

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
             # only if other reductionr are not doing anything
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
    #this visits |V| vertices
    v_visited[0] += G.vcount()
    #print(G)
    #deleted = list(range(len(degrees)))
    isolated = []
    #print(deleted)
    for i, v in enumerate(degrees):
        if (v == 0):
            isolated.append(G.vs[i])
            #deleted.append(G.vs[i]['original_index'])
            #G.delete_vertices(i)
    #this visits |V| vertices
    v_visited[0] += G.vcount()
    #
    # print(str(len(isolated)) + " isolated vertices")
    G.delete_vertices(isolated)
    #print("deleted vs: " + str(deleted))
    return G

def popular_v_reduction (G, k, solution, v_visited):
    degrees = G.degree(G.vs)

    # print("degrees: " + str(degrees))
    popular = []
    partial = []
    v_visited[0] += 2*G.vcount()
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

    v_visited[0] += 2*G.vcount()
    # for degree() and enumerate()

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

    v_visited[0] += 2*G.vcount()
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


#args: graph, size of VC param, current solution
#queue of vertices to check, vertices visited count
def local_reduction(G, k, solution, tbd, v_visited):
    print()
    print(G)
    taken = []
    partial = []
    q = set()
    for e in tbd:
        q.add(e)
        # G.vs[e]["deleted"] = True
    while(q):
        print("q: "+ str(q))
        #TODO : don't add if it's alreadyu in queue!
        #maybe sets?
        e = q.pop()
        print(e)
        print("v names: " + str(G.vs['name']))
        v = G.vs.find(str(e))
        print("v: " + str(v))
        d = G.degree(v)
        if(d == 0):
            print("deleting "+str(v) + " (isolated)")
            G.delete_vertices(v)
        if(d == 1):
            adj = G.neighbors(v)
            adj = adj[0]
            if(v not in partial):
                partial.append(G.vs[adj]['name'])
                #add neighbors of neighbor of pendant v to queue
                # print(adj)
                print(G.neighbors(G.vs[adj]))
                for e in G.neighbors(G.vs[adj]):
                    if(G.vs[e]['name'] != v['name']):
                        q.add(G.vs[e]['name'])
                #cannot delete both, bc can be in queue?
                #delete from queue as a solution
                q.discard(G.vs[adj]['name'])
                print("deleting "+str(v['name']  +str(G.vs[adj]['name'])))
                G.delete_vertices([v, adj])
        if(d == 2):
            adj = G.neighbors(v)
            if(G.get_eid(adj[0], adj[1], True, False) != -1):
                ap = [G.vs[adj[0]]['name'], G.vs[adj[1]]['name']]
                to_queue = G.neighborhood([G.vs[adj[0]], G.vs[adj[1]]])
                to_queue = [G.vs[item]['name'] for sublist in to_queue for item in sublist]
                to_queue = list(set(to_queue) - set([v, G.vs[adj[0]], G.vs[adj[1]]]))
                for e in to_queue:
                    q.add(e)
                partial.append(ap[0])
                partial.append(ap[1])
                print("deleting "+str(v['name'] + " " +str(G.vs[adj[0]]['name']))+ " " +str(G.vs[adj[1]]['name']))
                #delete from queue as a solution
                q.discard(G.vs[adj[0]]['name'])
                q.discard(G.vs[adj[1]]['name'])
                q.discard(v['name'])
                G.delete_vertices([v, G.vs[adj[0]], G.vs[adj[1]]])

            #else:
            #for merge 2 scenario
    solution |= set(partial)
    k -= len(partial)
    print(G)
    return G, k, solution
