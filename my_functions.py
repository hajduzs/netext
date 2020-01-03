import networkx as nx
import json
import re


def load_graph_form_json(path):
    with open(path) as file:
        data = json.load(file)
        G = nx.Graph()

        G.graph['name'] = data['name']

        for node in data['nodes']:
            G.add_node(node['id'])
            G.nodes[node['id']]['coords'] = tuple(node['coords'])

        for edge in data['edges']:
            G.add_edge(edge['from'], edge['to'])
            if 'points' in edge:
                G.edges[edge['from'], edge['to']]['points'] = [tuple(cd) for cd in edge['points']]

        return G


def generate_json_from_lgf(path, scale=1):
    file = open(path, 'r')
    all_line = file.read().split('\n')
    all_match = [re.findall(r'^(\d+)\t\((.+),(.+)\)|^(\d+)\t(\d+)\t(\d+)', line) for line in all_line]
    all_match = filter(len, all_match)
    nodes = []
    edges = []
    for line in all_match:
        line = line[0]
        if line[3] == '':
            c = "[" + str(float(line[1])*scale) + ", " + str(float(line[2])*scale) + "]"
            nodedata = "{ \"id\": \"" + line[0] + "\", \"coords\": " + c + " }"
            nodes.append(nodedata)
        else:
            edgedata = "{ \"from\": \"" + line[3] + "\", \"to\": \"" + line[4] + "\" }"
            edges.append(edgedata)

    json_data = "{ \"name\": \"" + path.split("/")[-1].split(".")[0] + "\", \"nodes\": ["

    for node in nodes:
        json_data += node + ","
    json_data = json_data[:-1]

    json_data += "], \"edges\": ["
    for edge in edges:
        json_data += edge + ","
    json_data = json_data[:-1]

    json_data += "] }"
    return json_data


def generate_json_from_gml(path, scale=1):

    G = nx.read_gml(path, label='id')

    node_data = G.nodes(data=True)
    edge_data = G.edges(data=True)

    nodes = []
    edges = []
    forbidden_nodes = []

    for node in node_data:
        if u'Longitude' not in [k for k, v in node[1].items()]:
            forbidden_nodes.append(node[0])
            continue
        c = "[" + str(node[1][u'Longitude'] * scale) + ", " + str(node[1][u'Latitude'] * scale) + "]"
        s = "{ \"id\": \"" + str(node[0]) + "\", \"coords\": " + c + " }"
        nodes.append(s)

    for edge in edge_data:
        if edge[0] in forbidden_nodes or edge[1] in forbidden_nodes:
            continue
        s = "{ \"from\": \"" + str(edge[0]) + "\", \"to\": \"" + str(edge[1]) + "\" }"
        edges.append(s)

    json_data = "{ \"name\": \"" + path.split("/")[-1].split(".")[0] + "\", \"nodes\": ["

    for node in nodes:
        json_data += node + ","
    json_data = json_data[:-1]

    json_data += "], \"edges\": ["
    for edge in edges:
        json_data += edge + ","
    json_data = json_data[:-1]

    json_data += "] }"

    return json_data


def calculateBoundingBox(graph, r=0, epsilon=0):
    if type(graph) != type(nx.Graph()): raise TypeError("parameter 'graph' is not the expected type! (nx.Graph)")

    all_points = [p[1]['coords'] for p in graph.nodes(data=True)]
    return returnBoundingBox(all_points, r, epsilon)


def returnBoundingBox(points, R, epsilon):
    Xmin = min(p[0] for p in points) - R - epsilon
    Ymin = min(p[1] for p in points) - R - epsilon
    Xmax = max(p[0] for p in points) + R + epsilon
    YMax = max(p[1] for p in points) + R + epsilon
    return {
        "x_min": Xmin,
        "y_min": Ymin,
        "x_max": Xmax,
        "y_max": YMax,
    }


def get_coords_for_node(node, graph):
    return graph.nodes[node]['coords']


def append_data_with_edge_chains(graph):
    if type(graph) != type(nx.Graph()): raise TypeError("parameter 'graph' is not the expected type! (nx.Graph)")
    for n1, n2, data in graph.edges(data=True):
        new_points = []
        new_points.append(get_coords_for_node(n2, graph))
        if 'points' in data:
            new_points.extend(data['points'])
        new_points.append(get_coords_for_node(n1, graph))
        data['points'] = new_points


def destringify_points(pts):
    points = []
    for p in pts.strip("\n").strip("  ").split("  "):
        xy = p.split(" ")
        points.append((float(xy[0]), float(xy[1])))
    return points


def stringify_points(points):
    ret = ""
    for p in points:
        ret += str(p[0]) + " " + str(p[1]) + "  "
    ret = ret.rstrip()
    return ret
