import json
import math
import re
import networkx as nx


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


def convert_lat_long_to_x_y(graph):
    candidate_nodes = [(node["coords"][0], node["coords"][1], node["id"]) for node in graph["nodes"]]

    avg_lon = sum([n[0] for n in candidate_nodes]) / len(candidate_nodes)
    avg_lat = sum([n[1] for n in candidate_nodes]) / len(candidate_nodes)

    new_nodes = []
    for n in candidate_nodes:
        dx = (avg_lon - n[0]) * 40000 * math.cos((avg_lat + n[1]) + math.pi / 360) / 360
        dy = (avg_lat - n[1]) * 40000 / 360
        new_nodes.append({
            "id": str(n[2]),
            "coords": [dx, dy]
        })

    graph["nodes"] = new_nodes


def generate_json_from_graphml(path):
    G = nx.read_graphml(path)
    nodes = []
    for n in G.nodes(data=True):
        nodes.append({
            "id": n[0],
            "coords": [
                n[1]['x'],
                n[1]['y']
            ]
        })

    edges = [{"from": e[0], "to": e[1]} for e in G.edges]

    return prep_graph_for_json_dump(path, nodes, edges)


def generate_json_from_lgf(path):
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
                    float(line[1]),
                    float(line[2])
                ]
            })
        else:
            edges.append({
                "from": str(line[3]),
                "to": str(line[4])
            })

    return prep_graph_for_json_dump(path, nodes, edges)


def generate_json_from_lgfll(path):
    g = generate_json_from_lgf(path)

    convert_lat_long_to_x_y(g)

    return g


def generate_json_from_ggml(path):
    G = nx.read_gml(path, label='id')

    node_data = G.nodes(data=True)
    edge_data = G.edges(data=True)

    nodes, edges = [], []

    for node_id, data in node_data:
        nodes.append({
            "id": str(node_id),
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


def generate_json_from_gml(path):
    G = nx.read_gml(path, label='id')

    node_data = G.nodes(data=True)
    edge_data = G.edges(data=True)

    nodes, edges, forbidden_nodes = [], [], []

    for node in node_data:
        if u'Longitude' not in [k for k, v in node[1].items()]:
            forbidden_nodes.append(node[0])
            continue

        nodes.append({
            "id": str(node[0]),
            "coords": [
                node[1][u'Longitude'],
                node[1][u'Latitude'],
            ]
        })

    for edge in edge_data:
        if edge[0] in forbidden_nodes or edge[1] in forbidden_nodes:
            continue
        edges.append({
            "from": str(edge[0]),
            "to": str(edge[1])
        })

    return_graph = prep_graph_for_json_dump(path, nodes, edges)

    convert_lat_long_to_x_y(return_graph)

    return return_graph


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
        for k, v in duplicates.items():
            dlist.append([k] + v)

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
        "nodes": nodes,  # _only_once,
        "edges": edges  # _repaired
    }
