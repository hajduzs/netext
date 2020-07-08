from algorithms import helper_functions as func
from algorithms.algoritmhs_helper_functions import compare_chosen_edges
from libs.Wrappers.PathPlanner import PathPlanner
import logging
import Utilities.Writer as l_out
import time
from Utilities.Timeit import Timeit


def heuristic_2(TOPOLOGY, DZL, CLI, BPD, R, g_r_path, PP, compare_model=None):

    logging.debug('-- Beginning HEURISTIC method.')
    start_time = time.time()
    Timeit.init()

    # HEUR step 1 (if done alone)
    # code MIGRATED to old_code.

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
            if d['bipartite'] == 0:
                neigh_cuts = [v for v in H.nodes if H.has_edge(n, v)]
                d["neigh"] = len(neigh_cuts)

    logging.debug('Minimum edge cover acquired.')
    logging.debug(f'Time needed: {time.time() - start_time}')
    start_time = time.time()

    # HEUR STEP 3: OPTIMIZING ON THESE NEW EDGES

    # get every danger zone that is avoided by two or more edges
    if False:
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

    alg_time = Timeit.time("heur_solution")

    l_out.write_paths("{}/{}".format(g_r_path, "heur_paths.txt"), chosen_edges)

    logging.debug(" ## Comparing HEURISTIC solution to actual lower bound:")

    if compare_model is not None:
        compare_chosen_edges(chosen_edges, CLI, compare_model, alg_time=alg_time, method="HEUR")

    return chosen_edges
