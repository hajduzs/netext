from algorithms.Pipeline import Pipeline

import mip
import itertools
import logging
from libs.Wrappers.PathPlanner import PathPlanner
from algorithms.detour_calc import calculate_path
from algorithms import helper_functions as func


def full_lp_calc(pl: Pipeline) -> (mip.Model, dict):
    logging.debug('Beginning FIRST LP method')

    # set up base path planner
    pp = PathPlanner()
    pp.setR(pl.r)
    for dz in pl.dzl:
        pp.addDangerZone(dz.string_poly)

    # set up model
    model = mip.Model()
    model.verbose = 0

    cs = dict()
    rhs = dict()

    # iterate over the bipartite graph
    number_of_lhs = len(pl.bpd.Edges)
    i = 0
    c_index = 0
    for n, d in pl.bpd.graph.nodes(data=True):
        if i < number_of_lhs:
            pnodes = d["vrtx"].edge
            pi = func.get_coords_for_node(pnodes[0], pl.topology)
            pg = func.get_coords_for_node(pnodes[1], pl.topology)

            nc = [v for v in pl.bpd.graph.neighbors(n)]
            p_cuts = itertools.chain.from_iterable(itertools.combinations(nc, r) for r in range(1, len(nc) + 1))

            for cuts in p_cuts:
                ids = set()
                for c in cuts:
                    ids.update(pl.bpd.return_ids_for_cut(c))
                    if c in rhs:
                        rhs[c].add(c_index)
                    else:
                        rhs[c] = set()
                        rhs[c].add(c_index)
                ids = list(ids)
                if len(ids) == 0:
                    continue

                pp_cost, pp_path = calculate_path(pi, pg, pl.r, pl.dzl, ids, pp)
                cs[c_index] = (model.add_var(var_type=mip.BINARY), pp_cost, pp_path, pnodes, list(cuts))
                c_index += 1

        else:
            model += mip.xsum([cs[k][0] for k in rhs[n]]) >= 1
        i += 1

    model.objective = mip.minimize(mip.xsum([c[0] * c[1] for i, c in cs.items()]))
    model.optimize()

    chosen = []
    for n, v in cs.items():
        if v[0].x == 1:
            i = int(n)  # int(n[7:-1])
            chosen.append((v[3], v[2], v[1], v[4]))
    return chosen

