import networkx as nx

from math import sqrt
from Utilities.Geometry2D import point_to_point, point_to_line, normal_vector


def node_hit_by(node, p, r):
    np = node[1]['coords']
    return point_to_point(np, p) <= r


def segment_hit_by(x, p1, p2, r):
    dist = point_to_line(x, p1, normal_vector(p1, p2))
    if dist > r:
        return False
    pa = point_to_point(x, p1)
    pb = point_to_point(x, p2)
    if pa <= r or pb <= r:
        return True
    if max(pa, pb) <= sqrt(r ** 2 + point_to_point(p1, p2) ** 2):
        return True
    return False


def edge_hit_by(edge, p, r):
    for i in range(0, len(edge[2]['points']) - 1):
        p1 = edge[2]['points'][i]
        p2 = edge[2]['points'][i + 1]
        if segment_hit_by(p, p1, p2, r):
            return True
    return False


def get_nodes_killed(p, r, graph):
    damaged = []
    for node in graph.nodes(data=True):
        if node_hit_by(node, p, r):
            damaged.append(node)
    return damaged


def get_links_killed(p, r, graph):
    damaged = []
    for edge in graph.edges(data=True):
        if edge_hit_by(edge, p, r):
            damaged.append(edge)
    return damaged


def hit_graph_with_disaster(topology, r, p):
    G = topology.copy()

    n = get_nodes_killed(p, r, G)
    G.remove_nodes_from([node for node, nodeData in n])

    e = get_links_killed(p, r, G)
    G.remove_edges_from(e)

    return G


'''
Ok, I feel like this needs an explanation.
1. If the remaining graph is connected, the examined face is not a danger zone by definition. 
2. If it is disconnected, and has more than 2 components, it is automatically valid.
3. If it has 2 components, and these components are not isolated points, it is valid.
4. If the isolated point's distance to any point of the danger zone is bigger than r * gamma 
   (where gamma is a parameter of tolerance), then it is indeed valid. 
5. If the polygon (danger zone) doesnt have points farther than r*gamma, it is dismissed.
'''
# TODO: clean up this unholy abomination


def is_face_valid_dangerzone(gamma, poly, r, graph):
    valid = False
    if not nx.is_connected(graph):
        # remove later
        return True
        if nx.number_connected_components(graph) == 2:
            xd = nx.connected_components(graph)
            cl = [c for c in nx.connected_components(graph) if len(c) == 1]
            if len(cl) != 0:
                c = cl[0]
                valid = False
                for x, y in poly.exterior.coords:
                    sp = [node for node in c.nodes(data=True)]
                    t = point_to_point(sp[0][1]["coords"], (x, y))
                    if t > r * gamma:
                        valid = True
                        break
            else:
                valid = True
        else:
            valid = True

    return valid

