import copy
from vc_preprocessing import *

def greedy_solution(g):
    solution = []
    while(len(g.es) != 0):
        v = max(enumerate(g.degree(), key= lambda x: x[1])) # get v of maximum degree
        print("max degree v: "+ v)
        solution.append(v['original_index'])
        g.delete_vertices(v)
    return solution

def get_maximal_matching(g, v_visited=[0]):
    matching_vs = set()
    # for e in g.es:
        # if( (not g.vs[e.target]['original_index'] in matching_vs ) and (not g.vs[e.source]['original_index'] in matching_vs) ):
        #     matching_vs.add(g.vs[e.target]['original_index'])
    v_visited[0] += len(g.vs)
    for i, e in enumerate(g.es):
        if (not (g.vs[e.target]['original_index'] in matching_vs))  and (not (g.vs[e.source]['original_index'] in matching_vs) ):
            #TODO does not add edges but vertices
            matching_vs.add(g.vs[e.target]['original_index'])
    return matching_vs, v_visited


def solve_degree_two(g, v_visited):
    print(" used degree two solver")
    covered = set()
    taken = set()
    v_visited[0] += len(g.vs)
    for v in g.vs:
        if(not v["original_index"] in covered):
            covered.add(v["original_index"])
            taken.add(v["original_index"])
            covered |= { g.vs[v]['original_index'] for v in g.neighbors(v)}

    return taken
def branch_and_reduce(g, solution, current_best_solution, k, args, v_visited):

    v_visited[0] += 1

    # DEGREE_TWO_SOLVER = True
    DEGREE_TWO_SOLVER = False
    # g, p_solution = no_param_preprocessing(g, solution)
    # print("KKKK:" + str(k))
    #
    # solver for degree-two Graphs
    if(g.vcount() and DEGREE_TWO_SOLVER):
        v_visited[0] += len(g.vs)
        v, degree = max(enumerate(g.degree()), key= lambda x: x[1]) # get v of maximum degree
        print("max degree : " + str(degree))
        if(degree <= 2 and DEGREE_TWO_SOLVER):
            return solution | solve_degree_two(copy.deepcopy(g), v_visited)

    if(args.optimization >= 3 and args.optimization < 5):
        g, k, solution = apply_preprocessing(g, k, solution, args, v_visited)
        #TODO: localised interleaving
    # print("after reductions:")
    # print("|V| = " + str(g.vcount()))
    # print("k = " + str(k))
    if(k < 0):
        # no-instance
        print("no-instance")
        return current_best_solution


    # print("solution after no param processing: ")
    # print(" after bnb preprocessing: " + str(len(solution)))
    # print(g.summary())
    if(args.optimization >= 1 ):
        lower_bound, v_visited = get_maximal_matching(copy.deepcopy(g), v_visited)
        # print("lwer bound: " + str(lower_bound))
        # print(len(lower_bound))
        if(len(solution) + len(lower_bound) >= len(current_best_solution) or len(lower_bound) > k):
            # print("current solution unchanged")
            return current_best_solution

    # if graph is empty ...
    # print(g.ecount())
    # TODO change lower bound
    if(g.ecount() == 0):
        # print("found partial size: " + str(len(set(solution) | lower_bound)))
        # print(set(solution) | lower_bound)
        return set(solution) #| lower_bound
    v, _ = max(enumerate(g.degree()), key= lambda x: x[1]) # get v of maximum degree
    #branch; b1 has taken v
    # print(str(v) + " is highest degree (" + str(g.vs[v]['original_index']))
    (b1, sol1,k1), (b2, sol2, k2) = branch(g, v, solution, k, v_visited, args)
    # print("new branches: ")
    # print(b1.summary())
    # print(b2.summary())

    # print(sol1)
    # print(sol2)
    # print([item for item in sol1 if item not in solution])
    # print([item for item in sol2 if item not in solution])
    current_best_solution = branch_and_reduce(b1, sol1, current_best_solution, k1, args, v_visited)
    current_best_solution = branch_and_reduce(b2, sol2, current_best_solution, k2, args, v_visited)
    return current_best_solution

def branch_and_bound(g, k, solution):
    v_visited = [2]
    solution = set()
    upper_bound = g.vcount()-1
    #instances = set()
    n = tuple()
    n = (g,solution,k)
    print(n)
    print(type(n))
    instances = set(n)
    current_best_solution = []
    while(len(instances) != 0):
        (c_graph, c_solution, c_k) = instances.pop()

        c_graph, c_k, c_solution = apply_preprocessing(g, k , solution, v_visited)
        #find maximal (greedy) matching
        matching_size = 0
        for v in c_graph.vs:
            v["matched"] = False
        for e in c_graph.es:
            if(c_graph.vs[e.target]["matched"] == False and c_graph.vs[e.source]["matched"] == False  ):
                c_graph.vs[e.target]["matched"] = True
                c_graph.vs[e.source]["matched"] = True
                matching_size += 1

        lower_bound = matching_size
        if(lower_bound > c_k):
            continue #this branch has no future
        
        if(lower_bound < upper_bound):
            solution_candidate = greedy_solution(c_graph)
            
            if(len(solution_candidate) < upper_bound):
                upper_bound = len(solution_candidate)
                current_best_solution = c_solution + [c_graph.vs[v]["original_index"] for v in solution_candidate]
                print("upper bound down to " + str(len(solution_candidate)))
            if(lower_bound < upper_bound):
                v = max(enumerate(g.degree()), key= lambda x: x[1]) # get v of maximum degree
                #branch; b1 has taken v
                b1, b2 = branch(g, v, c_solution, c_k)
                instances.add(b1)
                instances.add(b2)
    return current_best_solution

def branch(g, v, solution, k, v_visited, args):
    # copy is sloww
    v_visited[0] += 2*g.vcount()
    i_taken = copy.deepcopy(g)#g.copy()
    s1 = copy.deepcopy(solution)
    i_not_taken = copy.deepcopy(g)#g.copy()
    s2 = copy.deepcopy(solution)
    s1.add(g.vs[v]["original_index"])

    nbrs = g.neighbors(v)
    v_visited[0] += len(nbrs)

    for r in nbrs:
        s2.add(g.vs[r]["original_index"])

    if(args.optimization >= 5):
        to_check1 = g.neighbors(g.vs[v])
        to_check1 = [g.vs[v]['name'] for v in to_check1]
        to_check2 = g.neighborhood(g.neighbors(v))
        to_check2 = [g.vs[item]['name'] for sublist in to_check2 for item in sublist]
        to_check2 = list(set(to_check2) - set([str(g.vs[e]['name']) for e in g.neighborhood(v)]))
        print("check2: "+str(to_check2))
    i_taken.delete_vertices(v)
    # i_not_taken.delete_vertices(v)
    new_k = k-len(nbrs)
    # print(k)
    # print(len(g.neighbors(v)))
    # print("new_k: " + str(new_k))
    i_not_taken.delete_vertices((g.neighbors(v)+[v]))

    if(args.optimization >= 5):
        i_taken, k, s1  = local_reduction(i_taken, k, s1, to_check1, v_visited)
        i_not_taken, new_k, s2= local_reduction(i_not_taken, new_k, s2, to_check2, v_visited)

    return ((i_taken, s1, k-1), (i_not_taken, s2, new_k))

# old branch
# def branch(g, k, solution):
#     g, k, solution = apply_preprocessing(g, k, solution)
#     ecount = g.ecount()
#     vcount = g.vcount()
#     #print (g)
#     if(k < 0):
#         return 0
#     if(k == 0):
#         #print(g)
#         if(ecount == 0):
#             return solution
#         else:
#             return 0

#     if(ecount == 0):
#         #print(g)
#         return solution
#     pairs = ((i, j) for i in range(vcount) for j in range(vcount))
#     #TODO: randomize pairs
#     for i, j in pairs:
#         if(g.get_eid(i, j, True, False) != -1):
#             #two cases branch:
#             i_taken = g.copy()
#             i_not_taken = g.copy()
#             i_taken.delete_vertices(i)
#             i_not_taken.delete_vertices(g.neighbors(i))
#             deg =  g.degree(i)
#             org_vss = []
#             for v in g.neighbors(i):
#                 #print(g.vs[v]['original_index'])
#                 org_vss.append(g.vs[v]['original_index'])
#             sol_copy = copy.deepcopy(solution)
#             sol_copy.append(g.vs[i]['original_index'])

#             print("branch on " + str(g.vs[i]['original_index']) + " and " + str(org_vss))
#             #print(solution+org_vss)
#             #print(sol_copy)
#             # to free var? to test
#             # del g
#             return (branch(i_taken, k-1, sol_copy) or branch(i_not_taken, k-deg, solution+org_vss))
