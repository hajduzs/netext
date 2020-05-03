from algorithms import helper_functions as func
from Utilities.Geometry2D import point_to_point
from math import acos, pi
import logging


def get_ids_to_avoid(n, d, BPD, TOPOLOGY):
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
    return list(ids)


def compare_chosen(chosen_edges, TOPOLOGY, R, method):
    logging.debug(f' ## Comparing {method} edges:')

    for edge, path, cost, zones in chosen_edges:
        p_a = func.get_coords_for_node(edge[0], TOPOLOGY)
        p_b = func.get_coords_for_node(edge[1], TOPOLOGY)
        dist = point_to_point(p_a, p_b)
        if dist >= 2 * R:
            ub = 2.3 * R + 2 * dist
            diff = 100 * (cost / ub)
            logging.info(f'long - Compared {edge}. C: {cost} UB:{ub} - D: {diff}%')
        else:
            ub = 4 * pi * acos(dist / (2 * R))
            diff = 100 * (cost / ub)
            logging.info(f'short - Compared {edge}. C: {cost} UB:{ub} - D: {diff}%')

