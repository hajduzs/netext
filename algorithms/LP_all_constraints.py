from NetworkModels.ConstarintGraph import ConstraintGraph
from libs.Wrappers.PathPlanner import PathPlanner

from algorithms import helper_functions as func
import logging
import Utilities.Writer as l_out
import mip
import itertools


def linear_prog_method(TOPOLOGY, DZL, BPD, R, g_r_path, all_constr=True, constr_it=False):
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

    logging.info('LP solution:')
    for v in MODEL.vars:
        logging.info(f'{v.name} : {v.x}')

    for c in MODEL.constrs:
        if c.slack > 0 and (0 in [v for k, v in c.expr.expr.items()]):
            logging.warning(f'NON_ZERO_SLACK FOUND: {c}')

    # TODO: ide kell beszúrni, ha egy constr nem =re teljesül MODEL += <i_subs>

    CG = ConstraintGraph(MODEL.constrs)

    CG.print_data()

    chosen_edges = CG.optimize(CL)

    l_out.write_paths("{}/{}".format(g_r_path, "paths.txt"), chosen_edges)

    a_sum = 0  # actual sum
    for edge, path, cost, zones in chosen_edges:
        a_sum += cost
        lower_bound = sum([MODEL.vars[z_id].x for z_id in zones])
        logging.info(f'ids: {[z for z in zones]}')
        logging.info(f'compare done for edge {edge}. LB: {lower_bound} AC: {cost} .. diff: {cost - lower_bound} '
                     f'(+{100 * (cost - lower_bound) / lower_bound}%)')

    lb_sum = sum([MODEL.vars[i].x for i in range(0, len(DZL))])  # lower bound sum
    logging.info(f'In total: LB: {lb_sum}, AC: {a_sum} .. diff: {a_sum - lb_sum} (+{100 * (a_sum - lb_sum) / lb_sum}%)')

    return chosen_edges
