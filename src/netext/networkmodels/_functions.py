from math import sqrt
from typing import Tuple
from src.geometry.structures.Point import Point
from src.geometry.structures.Polygon import Polygon
from src.graphs.Topology import Topology
import src.geometry.operations_2d as op
import networkx as nx


def hit_graph_with_disaster(topology: Topology, p: Point, r: float) -> nx.Graph:
    # Make a copy of the graph, so we dont mess up the topology
    g = topology.graph.copy()

    # KILL nodes
    d_nodes = []
    for n in g.nodes():
        if op.point_to_point(p, topology.coords[n]) <= r:
            d_nodes.append(n)
    g.remove_nodes_from(d_nodes)

    # KILL edges
    d_edges = []
    for u, v in g.edges():
        d = op.point_to_line_abs(p, topology.coords[u], topology.coords[v])
        if d > r:
            continue
        pa = op.point_to_point(p, topology.coords[u])
        pb = op.point_to_point(p, topology.coords[v])
        cond1 = pa <= r or pb <= r
        cond2 = max(pa, pb) <= sqrt(r ** 2 + op.point_to_point(topology.coords[u], topology.coords[v]) ** 2)
        if cond1 or cond2:
            d_edges.append((u, v))
    g.remove_edges_from(d_edges)

    return g


# RETURNS valid (is valid), and omit (is omitted because of the gamma test):
def is_valid_danger_zone(topology: Topology, graph: nx.Graph, face: Polygon, r: float, gamma: float = 1.1) \
        -> Tuple[bool, int]:

    # If its connected, not a danger zone
    if nx.is_connected(graph):
        return False, 0

    # If the remaining graph has 3 or more components, it is a danger zone
    if nx.number_connected_components(graph) > 2:
        return True, 0

    # If there are 2 components, but none of them are isolated points, danger zone
    cl = [c for c in nx.connected_components(graph) if len(c) == 1]
    if len(cl) == 0:
        return True, 0

    # If the distance of the isolated point (c) to any outer point of the danger zone boundary
    # is greater than r * gamma, then it is valid, otherwise it is not (omitted because of the gamma test).
    isolated_node = topology.coords[cl[0].pop()]
    for ext_point in face:
        t = op.point_to_point(isolated_node, ext_point)
        if t > r * gamma:
            return True, 0

    return False, 1
