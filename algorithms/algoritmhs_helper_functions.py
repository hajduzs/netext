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

def compare_chosen_edges(chosen_edges, DZL, MODEL):
    a_sum = 0  # actual sum
    for edge, path, cost, zones in chosen_edges:
        a_sum += cost
        lower_bound = sum([MODEL.vars[z_id].x for z_id in zones])
        logging.info(f'ids: {[z for z in zones]}')
        logging.info(f'compare done for edge {edge}. LB: {lower_bound} AC: {cost} .. diff: {cost - lower_bound} '
                     f'(+{100 * (cost - lower_bound) / lower_bound}%)')

    lb_sum = sum([MODEL.vars[i].x for i in range(0, len(DZL))])  # lower bound sum
    if lb_sum != 0:
        change = 100 * (a_sum - lb_sum) / lb_sum
    else:
        change = -1
    logging.info(f'In total: LB: {lb_sum}, AC: {a_sum} .. diff: {a_sum - lb_sum} (+{change}%)')


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

