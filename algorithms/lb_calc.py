from algorithms.Pipeline import Pipeline

import mip
import itertools
import logging
from libs.Wrappers.PathPlanner import PathPlanner
from algorithms.detour_calc import calculate_path
from algorithms import helper_functions as func
from Utilities.Data import Info


def dual_lp_lb_calc(pl: Pipeline, full=True, iterate=False, c_limit=10**4) -> (mip.Model, dict):
    logging.debug('Beginning LP method')
    PP = PathPlanner()
    PP.setR(pl.r)
    for dz in pl.dzl:
        PP.addDangerZone(dz.string_poly)

    MODEL = mip.Model()
    MODEL.verbose = 0
    X = [MODEL.add_var(var_type=mip.CONTINUOUS) for i in range(0, len(pl.cl))]

    CL = {}
    c_index = 0
    c_powersets = {}

    for n, d in pl.bpd.graph.nodes(data=True):
        if d["bipartite"] == 1:
            continue

        pnodes = d["vrtx"].edge
        pi = func.get_coords_for_node(pnodes[0], pl.topology)
        pg = func.get_coords_for_node(pnodes[1], pl.topology)

        nc = [v for v in pl.bpd.graph.neighbors(n)]

        if full:
            p_cuts = itertools.chain.from_iterable(itertools.combinations(nc, r) for r in range(1, len(nc) + 1))
        else:
            p_cuts = [nc]

        for cuts in p_cuts:

            ids = set()
            for c in cuts:
                ids.update(pl.bpd.return_ids_for_cut(c))
            ids = list(ids)

            if len(ids) == 0:
                continue

            pp_cost, pp_path = calculate_path(pi, pg, pl.r, pl.dzl, ids, PP)

            MODEL += mip.xsum([X[k] for k in cuts]) <= pp_cost, str(c_index)
            c_powersets[str(c_index)] = pnodes
            CL[c_index] = pnodes, pp_path
            c_index += 1

    MODEL.objective = mip.maximize(mip.xsum(X))
    MODEL.optimize()

    if not full and iterate:
        tight_found = True
        c_limit = min(Info.get_instance().total_constraints, c_limit)
        while tight_found and c_index < c_limit:
            tight_found = False
            for c in MODEL.constrs:
                if c.slack > 0:
                    tight_found = True
                    pnodes = c_powersets[c.name]
                    cuts_in_constr = [int(k.name[4:-1]) for k in c.expr.expr]
                    minus_one_power_sets = itertools.combinations(cuts_in_constr, len(cuts_in_constr) - 1)

                    for cuts in [x for x in minus_one_power_sets]:
                        ids = set()
                        for c in cuts:
                            ids.update(pl.bpd.return_ids_for_cut(c))
                        ids = list(ids)

                        if len(ids) == 0:
                            continue
                        pi = func.get_coords_for_node(pnodes[0], pl.topology)
                        pg = func.get_coords_for_node(pnodes[1], pl.topology)
                        pp_cost, pp_path = calculate_path(pi, pg, pl.r, pl.dzl, ids, PP)

                        MODEL += mip.xsum([X[k] for k in cuts]) <= pp_cost, str(c_index)
                        c_powersets[str(c_index)] = pnodes
                        CL[c_index] = pnodes, pp_path
                        c_index += 1
                    MODEL.optimize()
        Info.get_instance().iter_completed = not tight_found
    return MODEL, CL
