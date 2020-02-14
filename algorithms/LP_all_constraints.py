from NetworkModels.ConstarintGraph import ConstraintGraph
from libs.Wrappers.PathPlanner import PathPlanner

import algorithms.algoritmhs_helper_functions as a_func
import helper_functions as func
import Utilities.Logging as logging

import mip
import itertools


def linear_prog_method(TOPOLOGY, DZL, BPD, R, g_r_path, all_constr=True):
    # SET UP PATH PLANNER

    PP = PathPlanner()
    PP.setR(R)

    # load danger zones into the path planner
    for dz in DZL:
        PP.addDangerZone(dz.string_poly)

    # TODO:
    # LP problem

    MODEL = mip.Model()
    X = [MODEL.add_var(var_type=mip.CONTINUOUS) for i in range(0, len(DZL))]

    # constraintek feltoltese

    CL = {}
    c_index = 0

    for n, d in BPD.graph.nodes(data=True):

        if d["bipartite"] == 1:
            continue

        # get ccordinates
        pnodes = d["vrtx"].edge
        pi = func.get_coords_for_node(pnodes[0], TOPOLOGY)
        pg = func.get_coords_for_node(pnodes[1], TOPOLOGY)

        # get adjacent danger zones
        neigh_cuts = [v for v in BPD.graph.nodes if BPD.graph.has_edge(n, v)]
        d["neigh"] = len(neigh_cuts)
        ids = set()
        for c in neigh_cuts:
            ids.update(BPD.return_ids_for_cut(c))
        ids = list(ids)

        if all_constr:
            i_subsets = itertools.chain.from_iterable(itertools.combinations(ids, r) for r in range(1, len(ids) + 1))
        else:
            i_subsets = [ids]

        for subs in i_subsets:
            PP.calculate_r_detour(pi, pg, subs)
            MODEL += mip.xsum([X[k] for k in subs]) <= PP.getCost()
            CL[c_index] = (pnodes, PP.getPath())
            c_index += 1

    MODEL.objective = mip.maximize(mip.xsum(X))

    # max egy percig fusson
    status = MODEL.optimize(max_seconds=60)

    print('solution:')
    for v in MODEL.vars:
        print('{} : {}'.format(v.name, v.x))

    CG = ConstraintGraph(MODEL.constrs)

    CG.print_data()

    chosen_edges = CG.optimize(CL)

    logging.write_paths("{}/{}".format(g_r_path, "paths.txt"), chosen_edges)

    acsum = 0
    for edge, path, cost, zones in chosen_edges:
        acsum += cost
        lowerbound = sum([MODEL.vars[id].x for id in zones])
        print("ids: {}".format([z for z in zones]))
        print("compare done for edge {}. LB: {} AC: {} .. diff: {} (+{}%)".format(edge, lowerbound, cost,
                                                                                  cost - lowerbound,
                                                                                  100 * (cost - lowerbound) / lowerbound))

    lbsum = sum([MODEL.vars[i].x for i in range(0, len(DZL))])
    print("In total: LB: {}, AC: {} .. diff: {} (+{}%)".format(lbsum, acsum, acsum - lbsum,
                                                               100 * (acsum - lbsum) / lbsum))

    return chosen_edges
