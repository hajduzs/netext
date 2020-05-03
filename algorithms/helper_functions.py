import networkx as nx
import json
import os
import logging

from algorithms.graph_reading import generate_json_from_graphml, generate_json_from_lgf, \
    generate_json_from_lgfll, generate_json_from_ggml, generate_json_from_gml


def create_output_directory(FILES, g):
    FILES['g_path'] = "output/{}".format(g.split('.')[0])  # gpath = output/test
    if not os.path.exists(FILES['g_path']):
        os.mkdir(FILES['g_path'])


def create_r_output_directory(FILES, R):
    FILES['g_r_path'] = FILES['g_path'] + "/r_{}".format(R)  # g_r_path = output/test/r_10
    os.mkdir(FILES['g_r_path'])

    FILES['g_r_path_data'] = FILES['g_r_path'] + "/data"
    os.mkdir(FILES['g_r_path_data'])

    # set Up logging
    fileh = logging.FileHandler(FILES['g_r_path'] + "/log.txt", 'w')
    formt = logging.Formatter('%(levelname)-8.8s%(message)s')
    fileh.setFormatter(formt)
    log = logging.getLogger()
    for hdlr in log.handlers[:]:  # remove all old handlers
        log.removeHandler(hdlr)
    log.addHandler(fileh)
    log.setLevel(logging.DEBUG)


def load_graph_names(FILES):
    gl = []
    for (dp, dn, filenames) in os.walk(FILES['input_dir']):
        gl.extend(filenames)
        break
    return gl


def generate_or_read_json(FILES, g):
    FILES['js_name'] = FILES['g_path'] + "/" + g.split(".")[0] + ".json"  # jsname = output/test/test.json
    if not os.path.exists(FILES['js_name']):
        js = None

        file_format = g.split('.')[1]
        input_file = FILES['input_dir'] + g

        if file_format == "lgf":
            js = generate_json_from_lgf(input_file)

        if file_format == "lgfll":
            js = generate_json_from_lgfll(input_file)

        if file_format == "gml":
            js = generate_json_from_gml(input_file)

        if file_format == "ggml":
            js = generate_json_from_ggml(input_file)

        if file_format == "graphml":
            js = generate_json_from_graphml(input_file)

        if js is None:
            logging.warning(f'Not supported file format for {g}. continuing as if nothing happened')
            return None

        with open(FILES['js_name'], "w") as f:
            f.write(json.dumps(js))

        return True
    else:
        return True  # if file already exists, all good


def calculate_bounding_box(graph, r=0, epsilon=0):
    if not isinstance(graph, nx.Graph):
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
    if not isinstance(graph, nx.Graph):
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
