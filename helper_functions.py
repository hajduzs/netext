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
            nodes.append({
                "id": str(line[0]),
                "coords": [
                    float(line[1]) * scale,
                    float(line[2]) * scale
                ]
            })
        else:
            edges.append({
                "from": str(line[3]),
                "to": str(line[4])
            })

    return prep_graph_for_json_dump(path, nodes, edges)

def generate_json_from_lgfll(path, scale=1):

    G = generate_json_from_lgf(path, scale)

    candidate_nodes = []

    for node in G["nodes"]:
        # Longitude-Latitude conversion
        candidate_nodes.append((
            node["coords"][0],
            node["coords"][1],
            node["id"]
        ))

    avg_lon = sum([n[0] for n in candidate_nodes]) / len(candidate_nodes)
    avg_lat = sum([n[1] for n in candidate_nodes]) / len(candidate_nodes)

    newnodes = []
    for n in candidate_nodes:
        dx = (avg_lon - n[0]) * 40000 * math.cos((avg_lat + n[1]) + math.pi / 360) / 360
        dy = (avg_lat - n[1]) * 40000 / 360
        print("converted {} to {}".format(n, (dx, dy)))
        newnodes.append({
            "id": str(n[2]),
            "coords": [
                dx * scale,
                dy * scale
            ]
        })

    G["nodes"] = newnodes
    return G


def generate_json_from_ggml(path, scale=1):
    G = nx.read_gml(path, label='id')

    node_data = G.nodes(data=True)
    edge_data = G.edges(data=True)

    nodes = []
    edges = []

    for id, data in node_data:
        nodes.append({
            "id": str(id),
            "coords": [
                data['graphics']['x'],
                data['graphics']['y'],
            ]
        })

    for n1, n2, data in edge_data:
        edges.append({
            "from": str(n1),
            "to": str(n2)
        })

    return prep_graph_for_json_dump(path, nodes, edges)


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
            node[1][u'Latitude'],
            node[0]
        ))

    avg_lon = sum([n[0] for n in candidate_nodes]) / len(candidate_nodes)
    avg_lat = sum([n[1] for n in candidate_nodes]) / len(candidate_nodes)

    for n in candidate_nodes:
        dx = (avg_lon - n[0]) * 40000 * math.cos((avg_lat + n[1]) + math.pi / 360) / 360
        dy = (avg_lat - n[1]) * 40000 / 360
        print("converted {} to {}".format(n, (dx, dy)))
        nodes.append({
            "id": str(n[2]),
            "coords": [
                dx * scale,
                dy * scale
            ]
        })

    for edge in edge_data:
        if edge[0] in forbidden_nodes or edge[1] in forbidden_nodes:
            continue
        edges.append({
            "from": str(edge[0]),
            "to": str(edge[1])
        })

    return prep_graph_for_json_dump(path, nodes, edges)


def node_already_in(n, nodes):
    for c in nodes:
        if n["coords"] == c["coords"]:
            return c["id"]
    return None


def prep_graph_for_json_dump(path, nodes, edges):

    if False:
        nodes_only_once = []
        duplicates = {}
        for n in nodes:
            ins = node_already_in(n, nodes_only_once)
            if ins is not None:
                if ins in duplicates:
                    duplicates[ins].append(n["id"])
                else:
                    duplicates[ins] = [n["id"]]
            else:
                nodes_only_once.append(n)



        dlist = []
        for k,v in duplicates.items():
            dlist.append( [k]+ v )

        edges_repaired = []

        for e in edges:
            f = e["from"]
            t = e["to"]
            for lst in dlist:
                if f in lst:
                    fi = lst.index(f)
                    dlfi = dlist.index(lst)
                if t in lst:
                    ti = lst.index(t)
                    dlti = dlist.index(lst)
            if dlfi == dlti:
                continue
            edges_repaired.append({
                "from": dlist[dlfi][0],
                "to": dlist[dlti][0]
            })


        print("weeded out duplicate nodes")

    return {
        "name": path.split("/")[-1].split(".")[0],
        "nodes": nodes,     # _only_once,
        "edges": edges      # _repaired
    }


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

        #try:

        if g.split('.')[1] == "lgf":
            js = generate_json_from_lgf(FILES['input_dir'] + g, scale)

        if g.split('.')[1] == "lgfll":
            js = generate_json_from_lgfll(FILES['input_dir'] + g, scale)

        if g.split('.')[1] == "gml":
            js = generate_json_from_gml(FILES['input_dir'] + g, scale)

        if g.split('.')[1] == "ggml":
            js = generate_json_from_ggml(FILES['input_dir'] + g, scale)

        #except:
        #    log("could not read {}".format(FILES['js_name'], "INPUT")

        if js is None:
            log("Not supported file format for {}. continuing as if nothing happened".format(g), "INPUT")
            return None

        with open(FILES['js_name'], "w") as f:
            f.write(json.dumps(js))

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



