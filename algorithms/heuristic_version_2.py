import helper_functions as func
import algorithms.algoritmhs_helper_functions as a_func
from libs.Wrappers.PathPlanner import PathPlanner


def heuristic_2(TOPOLOGY, DZL, BPD, R):

    PP = PathPlanner()
    PP.setR(R)

    # load danger zones into the path planner
    for dz in DZL:
        PP.addDangerZone(dz.string_poly)

    for n, d in BPD.graph.nodes(data=True):

        if d["bipartite"] == 1:
            return None

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

    # HEUR STEP 3: OPTIMIZING ON THESE NEW EDGES

    # get every danger zone that is avoided by two or more edges

    multiples = set()
    for i in range(0, len(nodes)):
        for j in range(i + 1, len(nodes)):
            multiples.update(nodes[i][1]["ids"].intersection(nodes[j][1]["ids"]))

    for Z in multiples:
        # get corresponding edges
        corr = [n for n in nodes if Z in n[1]["ids"]]
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
        min_d = 0
        # select minimal cost edge
        mincost = float("inf")
        for n, d in corr:
            if mincost > d["cost"] - d["t_cost"]:
                mincost = d["cost"] - d["t_cost"]
                min_n = n
                min_d = d

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

    # 4. AFTERWORK: only the selected edges (nodes) need to be in the graph.

    evs_to_remove = set(BPD.graph.nodes) - set([n for n, d in nodes])
    BPD.graph.remove_nodes_from(evs_to_remove)