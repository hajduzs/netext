from algorithms import Pipeline
from libs.Wrappers.PathPlanner import PathPlanner
from algorithms import helper_functions as func
import logging


def calc_edge_costs(BPD, H, TOPOLOGY, PP):
    to_remove = []
    for n, d in H.nodes(data=True):
        if d["bipartite"] == 1:
            continue
        # get ccordinates
        pnodes = d["vrtx"].edge
        pi = func.get_coords_for_node(pnodes[0], TOPOLOGY)
        pg = func.get_coords_for_node(pnodes[1], TOPOLOGY)
        # get adjacent cuts
        neigh_cuts = [v for v in H.neighbors(n)]
        if len(neigh_cuts) == 0:
            to_remove.append(n)
            continue
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
    H.remove_nodes_from(to_remove)


def __A(H):
    return min(dict(H.nodes).items(), key=lambda x: x[1]["cost"] / x[1]["neigh"])


def __C(H):
    return min(dict(H.nodes).items(), key=lambda x: x[1]["cost"])


def __N(H):
    return max(dict(H.nodes).items(), key=lambda x: (x[1]["neigh"], -x[1]["cost"]))  # max neigh, then cost


_edge_choosers = {
    'A': __A,
    'C': __C,
    'N': __N,
}


def heuristic_calc(p: Pipeline, method: str):
    # STEP 0 :: INITIALISE copy-paste variables
    TOPOLOGY = p.topology
    DZL = p.dzl
    BPD = p.bpd
    R = p.r
    # STEP 0.5 :: set up edge chooser:
    choose_edge = _edge_choosers[method]
    # STEP 1 :: Initialize the graph
    PP = PathPlanner()
    PP.setR(R)
    # load danger zones into the path planner
    for dz in DZL:
        PP.addDangerZone(dz.string_poly)

    H = BPD.graph.copy()
    calc_edge_costs(BPD, H, TOPOLOGY, PP)

    nodes = []
    # STEP 2 :: get edges from corresponding heuristic
    while True:
        if len(dict(H.nodes).items()) == 0:
            break
        maxn = choose_edge(H)

        nodes.append((maxn[1]['vrtx'].edge, maxn[1]['path'],
                      maxn[1]['cost'],  list(maxn[1]['ids'])))

        # delete cuts protected and node selected

        H.remove_nodes_from([v for v in H.neighbors(maxn[0])])
        H.remove_node(maxn[0])

        calc_edge_costs(BPD, H, TOPOLOGY, PP)

    return nodes