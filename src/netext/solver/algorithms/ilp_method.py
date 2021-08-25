import mip
import itertools
import logging

from src.geometry.pathfinder.path import PathPlanner
from src.netext.Pipeline import Pipeline
from src.netext.solver.detour_calc import calculate_path


def dual_lp_lb_calc(pl: Pipeline, full=True):
    logging.debug('Beginning LP method')
    pp = PathPlanner()
    pp.setR(pl.r)
    for dz in pl.dzl:
        pp.addDangerZone(dz.polygon.convert_to_str())

    model = mip.Model()
    model.verbose = 0
    variables = [model.add_var(var_type=mip.CONTINUOUS)] * len(pl.cl)

    cl = {}
    c_index = 0
    c_power_sets = {}

    for n, d in pl.bpd.graph.nodes(data=True):
        if d["bipartite"] == 1:
            continue

        nodes = n.split("/")
        pi = pl.topology.coords[nodes[0]]
        pg = pl.topology.coords[nodes[1]]

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

            pp_cost, pp_path = calculate_path(pi, pg, pl.r, pl.dzl, ids, pp)

            model += mip.xsum([variables[k] for k in cuts]) <= pp_cost, str(c_index)
            c_power_sets[str(c_index)] = nodes
            cl[c_index] = nodes, pp_path
            c_index += 1

    model.objective = mip.maximize(mip.xsum(variables))
    model.optimize()
    return model, cl
