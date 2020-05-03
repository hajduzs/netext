from algorithms import helper_functions as func
from libs.Wrappers.PathPlanner import PathPlanner
import logging
import Utilities.Writer as l_out
import time


def heuristic_2(TOPOLOGY, DZL, BPD, R, g_r_path, compare_model=None):

    logging.debug('-- Beginning HEURISTIC method.')
    start_time = time.time()

    PP = PathPlanner()
    PP.setR(R)

    # load danger zones into the path planner
    for dz in DZL:
        PP.addDangerZone(dz.string_poly)

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

        # calculate cost
        PP.calculate_r_detour(pi, pg, ids)
        cost = PP.getCost()
        path = PP.getPath()

        # update node
        d["path"] = path
        d["cost"] = cost
        d["ids"] = set(ids)

    logging.debug('BPD loaded with costs.')
    logging.debug(f'Time needed: {time.time() - start_time}')
    start_time = time.time()

    # HEUR STEP 2: get minimum edge cover
    H = BPD.graph.copy()

    nodes = []
    while True:
        if len(dict(H.nodes).items()) == 0:
            break
        maxn = max(dict(H.nodes).items(), key=lambda x: (x[1]["neigh"], -x[1]["cost"]))  # max neigh, then cost
        if maxn[1]["neigh"] == 0:
            break
        nodes.append(maxn)

        # delete cuts protected and node selected

        H.remove_nodes_from([v for v in H.nodes if H.has_edge(maxn[0], v)])
        H.remove_node(maxn[0])

        for n, d in H.nodes(data=True):
            if d['bipartite'] is 0:
                neigh_cuts = [v for v in H.nodes if H.has_edge(n, v)]
                d["neigh"] = len(neigh_cuts)

    logging.debug('Minimum edge cover acquired.')
    logging.debug(f'Time needed: {time.time() - start_time}')
    start_time = time.time()

    # HEUR STEP 3: OPTIMIZING ON THESE NEW EDGES

    # get every danger zone that is avoided by two or more edges

    multiples = set()
    for i in range(0, len(nodes)):
        for j in range(i + 1, len(nodes)):
            multiples.update(nodes[i][1]["ids"].intersection(nodes[j][1]["ids"]))

    rep_count = 0
    for Z in multiples:
        # get corresponding edges
        corr = [n for n in nodes if Z in n[1]["ids"]]
        rep_count += len(corr) - 1
        # set theoretical new edge cost and path for all (not containing Z)
        for n, d in corr:
            # get coordinates
            pnodes = d["vrtx"].edge
            pi = func.get_coords_for_node(pnodes[0], TOPOLOGY)
            pg = func.get_coords_for_node(pnodes[1], TOPOLOGY)

            # get adjacent danger zones
            neigh_cuts = [v for v in BPD.graph.nodes if BPD.graph.has_edge(n, v)]
            ids = set()
            no_removal = True
            for c in neigh_cuts:
                ids.update(BPD.return_ids_for_cut(c))
                if Z in ids:
                    ids.remove(Z)
                    no_removal = False
            if no_removal:
                break
            ids = list(ids)

            # calculate cost
            PP.calculate_r_detour(pi, pg, ids)
            cost = PP.getCost()
            path = PP.getPath()

            # update node
            d["t_path"] = path
            d["t_cost"] = cost
            d["t_ids"] = set(ids)

            print("{} {}".format(n, (d["cost"], d["ids"])))
            print("{} {}".format(n, (d["t_cost"], d["t_ids"])))
            print("diff: {}".format(d["cost"] - d["t_cost"]))

        min_n = 0
        # select minimal cost edge
        mincost = float("inf")
        for n, d in corr:
            if mincost > d["cost"] - d["t_cost"]:
                mincost = d["cost"] - d["t_cost"]
                min_n = n

        # set that in the graph
        for n, d in corr:
            if n == min_n:
                continue
            BPD.graph.nodes[n]["cost"] = d["t_cost"]
            BPD.graph.nodes[n]["path"] = d["t_path"]
            BPD.graph.nodes[n]["ids"] = d["t_ids"]

        # delete other edges
        for n, d in corr:
            if n == min_n:
                continue
            for v in [v for v in BPD.graph.nodes if BPD.graph.has_edge(n, v) and Z in BPD.return_ids_for_cut(v)]:
                BPD.graph.remove_edge(n, v)

    logging.debug(f'Optimized on chosen edges. Multiples: ({len(multiples)}), opt: ({rep_count})')
    logging.debug(f'Time needed: {time.time() - start_time}')
    start_time = time.time()

    # 4. AFTERWORK: only the selected edges (nodes) need to be in the graph.

    evs_to_remove = set(BPD.graph.nodes) - set([n for n, d in nodes])
    BPD.graph.remove_nodes_from(evs_to_remove)

    logging.debug(f'Deleted edges not used. ({len(evs_to_remove)})')
    logging.debug(f'Time needed: {time.time() - start_time}')

    chosen_edges = []

    for n, d in BPD.graph.nodes(data=True):
        chosen_edges.append((d['vrtx'].edge, d['path'], d['cost'],  list(d['ids'])))

    # edge, path, cost, zones
    # ( (1, 2), 'path', 311.01, [2,3] )

    l_out.write_paths("{}/{}".format(g_r_path, "heur_paths.txt"), chosen_edges)

    logging.debug(" ## Comparing HEURISTIC solution to actual lower bound:")

    if compare_model is not None:
        a_sum = 0  # actual sum
        for edge, path, cost, zones in chosen_edges:
            a_sum += cost
            lower_bound = sum([compare_model.vars[z_id].x for z_id in zones])
            logging.info(f'ids: {[z for z in zones]}')
            logging.info(f'compare done for edge {edge}. LB: {lower_bound} AC: {cost} .. diff: {cost - lower_bound} '
                         f'(+{100 * (cost - lower_bound) / lower_bound}%)')

        lb_sum = sum([compare_model.vars[i].x for i in range(0, len(DZL))])  # lower bound sum
        logging.info(
            f'In total: LB: {lb_sum}, AC: {a_sum} .. diff: {a_sum - lb_sum} (+{100 * (a_sum - lb_sum) / lb_sum}%)')

    #return chosen_edges