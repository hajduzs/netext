import networkx as nx
import json
import re
import os
import math

from Utilities.Logging import set_out,log


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
            c = "[" + str(float(line[1]) * scale) + ", " + str(float(line[2]) * scale) + "]"
            nodes.append("{ \"id\": \"" + line[0] + "\", \"coords\": " + c + " }")
        else:
            edges.append("{ \"from\": \"" + line[3] + "\", \"to\": \"" + line[4] + "\" }")

    return construct_json(path, nodes, edges)


def generate_json_from_gml(path, scale=1):
    G = nx.read_gml(path, label='id')

    node_data = G.nodes(data=True)
    edge_data = G.edges(data=True)

    candidate_nodes = []
    nodes = []
    edges = []
    forbidden_nodes = []

    for node in node_data:
        if u'Longitude' not in [k for k, v in node[1].items()]:
            forbidden_nodes.append(node[0])
            continue

        # Longitude-Latitude conversion
        candidate_nodes.append((
            node[1][u'Longitude'],
            node[1][u'Latitude']
        ))

    avg_lon = sum([n[0] for n in candidate_nodes]) / len(candidate_nodes)
    avg_lat = sum([n[1] for n in candidate_nodes]) / len(candidate_nodes)

    for n in candidate_nodes:
        dx = (avg_lon - n[0]) * 40000 * math.cos((avg_lat + n[1]) + math.pi / 360) / 360
        dy = (avg_lat - n[1]) * 40000 / 360
        print("converted {} to {}".format(n, (dx, dy)))
        nodes.append((dx, dy))

    for node in nodes:
        c = "[" + str(node[0] * scale) + ", " + str(node[0] * scale) + "]"
        s = "{ \"id\": \"" + str(node[0]) + "\", \"coords\": " + c + " }"
        nodes.append(s)

    for edge in edge_data:
        if edge[0] in forbidden_nodes or edge[1] in forbidden_nodes:
            continue
        s = "{ \"from\": \"" + str(edge[0]) + "\", \"to\": \"" + str(edge[1]) + "\" }"
        edges.append(s)

    return construct_json(path, nodes, edges)


def construct_json(path, nodes, edges):
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


def create_output_directory(FILES, g):
    FILES['g_path'] = "output/{}".format(g.split('.')[0])  # gpath = output/test
    if not os.path.exists(FILES['g_path']):
        os.mkdir(FILES['g_path'])


def create_r_output_directory(FILES, R):
    FILES['g_r_path'] = FILES['g_path'] + "/r_{}".format(R)  # g_r_path = output/test/r_10
    os.mkdir(FILES['g_r_path'])

    FILES['g_r_path_data'] = FILES['g_r_path'] + "/data"
    os.mkdir(FILES['g_r_path_data'])

    set_out(FILES['g_r_path'] + "/log.txt")


def load_graph_names(FILES):
    gl = []
    for (dp, dn, filenames) in os.walk(FILES['input_dir']):
        gl.extend(filenames)
        break
    return gl


def generate_or_read_json(FILES, scale, g):

    FILES['js_name'] = FILES['g_path'] + "/" + g.split(".")[0] + ".json"  # jsname = output/test/test.json
    if not os.path.exists(FILES['js_name']):
        js = None

        try:

            if g.split('.')[1] == "lgf":
                js = generate_json_from_lgf(FILES['input_dir'] + g, scale)

            if g.split('.')[1] == "gml":
                js = generate_json_from_gml(FILES['input_dir'] + g, scale)

        except:
            log("could not read {}", "INPUT")

        if js is None:
            log("Not supported file format for {}. continuing as if nothing happened".format(g), "INPUT")
            return None

        with open(FILES['js_name'], "w") as f:
            f.write(js)

        return True
    else:
        return True     # if file already exists, all good


def calculateBoundingBox(graph, r=0, epsilon=0):
    if type(graph) != type(nx.Graph()):
        raise TypeError("parameter 'graph' is not the expected type! (nx.Graph)")

    points = [p[1]['coords'] for p in graph.nodes(data=True)]

    ret = {
        "x_min": min(p[0] for p in points) - r - epsilon,
        "y_min": min(p[1] for p in points) - r - epsilon,
        "x_max": max(p[0] for p in points) + r + epsilon,
        "y_max": max(p[1] for p in points) + r + epsilon,
    }
    ret["small_side"] = min(ret["x_max"] - ret["x_min"], ret["y_max"] - ret["y_min"])
    return ret


def get_coords_for_node(node, graph):
    return graph.nodes[node]['coords']


def append_data_with_edge_chains(graph):
    if type(graph) != type(nx.Graph()):
        raise TypeError("parameter 'graph' is not the expected type! (nx.Graph)")

    for n1, n2, data in graph.edges(data=True):
        new_points = [get_coords_for_node(n2, graph)]
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
