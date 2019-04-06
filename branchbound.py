import copy
from vc_preprocessing import *
def branch(g, k, solution):
    g, k, solution = apply_preprocessing(g, k, solution)
    ecount = g.ecount()
    vcount = g.vcount()
    #print (g)
    if(k < 0):
        return 0
    if(k == 0):
        #print(g)
        if(ecount == 0):
            return solution
        else:
            return 0

    if(ecount == 0):
        #print(g)
        return solution
    pairs = ((i, j) for i in range(vcount) for j in range(vcount))
    #TODO: randomize pairs
    for i, j in pairs:
        if(g.get_eid(i, j, True, False) != -1):
            #two cases branch:
            i_taken = g.copy()
            i_not_taken = g.copy()
            i_taken.delete_vertices(i)
            i_not_taken.delete_vertices(g.neighbors(i))
            deg =  g.degree(i)
            org_vss = []
            for v in g.neighbors(i):
                #print(g.vs[v]['original_index'])
                org_vss.append(g.vs[v]['original_index'])
            sol_copy = copy.deepcopy(solution)
            sol_copy.append(g.vs[i]['original_index'])

            print("branch on " + str(g.vs[i]['original_index']) + " and " + str(org_vss))
            #print(solution+org_vss)
            #print(sol_copy)
            # to free var? to test
            # del g
            return (branch(i_taken, k-1, sol_copy) or branch(i_not_taken, k-deg, solution+org_vss))
