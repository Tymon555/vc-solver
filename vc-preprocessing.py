#!/usr/bin/env python

def isolated_v_reduction(G):
    degrees = G.degree(G.vs)
    deleted = []
    for i, v in enumerate(degrees):
        if (v == 0):
            deleted.append(v['original_index'])
            G.delete_vertices(v[i])
    print("deleted vs: " + str(deleted))
    return G
