from src.geometry.pathfinder.path import PathPlanner
from src.netext.Pipeline import Pipeline
from src.netext.solver.detour_calc import calculate_path


def best_avg_cost(bpd):
    return min(dict(bpd.nodes).items(),
               key=lambda x: x[1]["cost"] / x[1]["neigh"])


def best_cost(bpd):
    return min(dict(bpd.nodes).items(),
               key=lambda x: x[1]["cost"])


def most_cuts_protected(bpd):
    return max(dict(bpd.nodes).items(),
               key=lambda x: (x[1]["neigh"], -x[1]["cost"]))


_edge_choosers = {
    'A': best_avg_cost,
    'C': best_cost,
    'N': most_cuts_protected,
}


def calc_edge_costs(BPD, H, TOPOLOGY, r, dzl, PP):
    to_remove = []
    for n, d in H.nodes(data=True):
        if d["bipartite"] == 1:
            continue
        # get coordinates
        nodes = n.split("/")
        pi = TOPOLOGY.coords[nodes[0]]
        pg = TOPOLOGY.coords[nodes[1]]
        # get adjacent cuts
        neigh_cuts = [v for v in H[n]]
        if len(neigh_cuts) == 0:
            to_remove.append(n)
            continue
        d["neigh"] = len(neigh_cuts)
        ids = set()
        for c in neigh_cuts:
            ids.update(BPD.return_ids_for_cut(c))
        ids = list(ids)
        # calculate cost
        pp_cost, pp_path = calculate_path(pi, pg, r, dzl, ids, PP)
        # update node
        d["path"] = pp_path
        d["cost"] = pp_cost
        d["ids"] = set(neigh_cuts)
    H.remove_nodes_from(to_remove)


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
        PP.addDangerZone(dz.polygon.convert_to_str())

    BPD.init_attributes()
    H = BPD.graph.copy()

    calc_edge_costs(BPD, H, TOPOLOGY, R, DZL, PP)

    chosen_edges = []

    # STEP 2 :: get edges from corresponding heuristic
    while len(dict(H.nodes).items()) != 0:
        edge_choice = choose_edge(H)
        chosen_edges.append(
            (edge_choice[0],
             edge_choice[1]['path'],
             edge_choice[1]['cost'],
             list(edge_choice[1]['ids'])
             )
        )

        # delete cuts protected and node selected
        H.remove_nodes_from([v for v in H[edge_choice[0]]])
        H.remove_node(edge_choice[0])

        # re-calculate the costs accordingly
        calc_edge_costs(BPD, H, TOPOLOGY, R, DZL, PP)

    # we are done, good night

    return chosen_edges
