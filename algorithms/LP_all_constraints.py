from NetworkModels.ConstarintGraph import ConstraintGraph
from algorithms.algoritmhs_helper_functions import compare_chosen_edges
from libs.Wrappers.PathPlanner import PathPlanner

from algorithms.detour_calc import calculate_path
from algorithms import helper_functions as func
import logging
import Utilities.Writer as l_out
import mip
import itertools
import time
import progressbar


def linear_prog_method(TOPOLOGY, DZL, CLI, BPD, R, g_r_path):
    # SET UP PATH PLANNER

    logging.debug(f' -- Beginning LP method.')

    PP = PathPlanner()
    PP.setR(R)

    # load danger zones into the path planner
    for dz in DZL:
        PP.addDangerZone(dz.string_poly)

    # LP problem

    MODEL = mip.Model()
    X = [MODEL.add_var(var_type=mip.CONTINUOUS) for i in range(0, len(CLI))]

    # constraintek feltoltese

    start_time = time.time()

    CL = {}
    c_index = 0

    bar = progressbar.ProgressBar(maxval=BPD.num_path_calls(),
                      widgets=["paths: ", progressbar.Percentage(),
                               progressbar.Bar('=', '[', ']', ' ', ),
                               progressbar.SimpleProgress(), " ",
                               progressbar.ETA()
                               ]
                                  )
    bar.start()
    num_calls = 0
    for n, d in BPD.graph.nodes(data=True):

        if d["bipartite"] == 1:
            continue

        # get ccordinates
        pnodes = d["vrtx"].edge
        pi = func.get_coords_for_node(pnodes[0], TOPOLOGY)
        pg = func.get_coords_for_node(pnodes[1], TOPOLOGY)

        # get adjacent cuts
        nc = [v for v in BPD.graph.neighbors(n)]   # neighbouring cuts

        d["neigh"] = len(nc)

        p_cuts = itertools.chain.from_iterable(itertools.combinations(nc, r) for r in range(1, len(nc) + 1))

        for cuts in p_cuts:

            ids = set()
            for c in cuts:
                ids.update(BPD.return_ids_for_cut(c))
            ids = list(ids)

            #PP.calculate_r_detour(pi, pg, ids)
            #pp_cost = PP.getCost()
            #pp_path = PP.getPath()

            if len(ids) == 0:
                continue

            num_calls += 1
            bar.update(num_calls)

            pp_cost, pp_path = calculate_path(pi, pg, R, DZL, ids, PP)

            d["path"] = pp_path
            d["cost"] = pp_cost
            d["ids"] = set(cuts)

            MODEL += mip.xsum([X[k] for k in cuts]) <= pp_cost
            CL[c_index] = (pnodes, pp_path)
            c_index += 1

    bar.finish()
    logging.debug('Constraint graph updated from BPD.')
    logging.debug(f'Time needed: {time.time() - start_time}')
    start_time = time.time()

    MODEL.objective = mip.maximize(mip.xsum(X))

    # TODO: make it silent (verbose, no output)
    status = MODEL.optimize(max_seconds=60)

    logging.debug('LP Solution calculated.')
    logging.debug(f'Time needed: {time.time() - start_time}')
    start_time = time.time()

    logging.info('LP solution:')
    for v in MODEL.vars:
        logging.info(f'{v.name} : {v.x}')

    for c in MODEL.constrs:
        if c.slack > 0 and (0 in [v for k, v in c.expr.expr.items()]):
            logging.warning(f'NON_ZERO_SLACK FOUND: {c}')

    # TODO: ide kell beszúrni, ha egy constr nem =re teljesül MODEL += <i_subs>

    MODEL.write(f'{g_r_path}/model.lp')

    CG = ConstraintGraph(MODEL.constrs)

    CG.print_data()

    chosen_edges = CG.optimize(CL)

    l_out.write_paths("{}/{}".format(g_r_path, "lp_paths.txt"), chosen_edges)

    logging.debug(" ## Comparing LP solution to actual lower bound:")
    compare_chosen_edges(chosen_edges, CLI, MODEL, method="LP")

    return MODEL, PP, chosen_edges
