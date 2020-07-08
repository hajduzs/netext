import networkx as nx
import json
import os
import logging
import math
import itertools
import shapely.geometry as sg

import Utilities.Geometry2D as geom
import random
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
    formt = logging.Formatter('%(levelname)-9.9s%(message)s')
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
    gl.sort()
    return gl


def get_bounds(points):
    ret = {
        "x_min": min(p['coords'][0] for p in points),
        "y_min": min(p['coords'][1] for p in points),
        "x_max": max(p['coords'][0] for p in points),
        "y_max": max(p['coords'][1] for p in points)
    }
    return ret


def scale_js_graph(js, scale_to=10**4, left_bottom=(0, 0), integer=True):
    bb = get_bounds(js['nodes'])
    diff_x = left_bottom[0] - bb['x_min']
    diff_y = left_bottom[1] - bb['y_min']
    scale_factor = scale_to / max(bb['x_max'] + diff_x, bb['y_max'] + diff_y)
    js['scale_factor'] = scale_factor
    for p in js['nodes']:
        p['coords'] = [
            (p['coords'][0] + diff_x) * scale_factor,
            (p['coords'][1] + diff_y) * scale_factor,
        ]
    if integer:
        for p in js['nodes']:
            p['coords'] = [
                int(p['coords'][0]),
                int(p['coords'][1])
            ]


def generate_or_read_json(FILES, g):
    FILES['js_name'] = FILES['g_path'] + "/" + g.split(".")[0] + ".json"  # jsname = output/test/test.json
    if not os.path.exists(FILES['js_name']):
        js = None

        file_format = g.split('.')[1]
        input_file = FILES['input_dir'] + g

        try:

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
        except nx.NetworkXError as e:
            js = None
        except Exception as e:
            js = None

        if js is None:
            logging.warning(f'Not supported file format for {g}. continuing as if nothing happened')
            return None

        scale_js_graph(js)

        with open(FILES['js_name'], "w") as f:
            f.write(json.dumps(js))

        return True
    else:
        return True  # if file already exists, all good


def sample_point(poly: sg.Polygon):
    if not poly.is_valid:
        poly = poly.buffer(0)
        if poly.is_empty:
            return None
    try:
        p = poly.representative_point()
    except Exception as e:
        p = None
    return p
    '''
    minx, miny, maxx, maxy = poly.bounds
    while True:
        p = sg.Point(random.uniform(minx, maxx), random.uniform(miny, maxy))
        if poly.contains(p):
            return p
    '''


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
    if node[:3] != "rep":
        return graph.nodes[node]['coords']
    else:
        d = node.split("-")   # [[e1, e2],id]
        en = d[0].split("_")
        e1 = en[0][3:]
        e2 = en[1]
        id = int(d[1])
        return graph[e1][e2]['repeaters'][id][1]


def get_repeaters_from_edge_list(topology, edgelist):
    rep = []
    for a, b in edgelist:
        rep.extend([r[0] for r in topology[a][b]['repeaters']])
    for r in rep:
        print(r)
    return rep


def get_live_edges_from_set(topology, nodeset):
    combinations = itertools.combinations(nodeset, 2)
    ret = []
    for c in combinations:
        if topology.has_edge(*c):
            ret.append(c)
    return ret


def get_connetion_points_from_node_set(topology, nodeset):
    rep = get_repeaters_from_edge_list(topology,get_live_edges_from_set(topology, nodeset))
    rep.extend(nodeset)
    return rep


def append_topology_with_repeaters(topology, distance):
    tiny = float(10 ** -10)
    for a, b, data in topology.edges(data=True):
        p1 = data['points'][0]
        p2 = data['points'][1]
        alpha = geom.angle_between(p1, p2)
        diff_x = distance * math.cos(alpha)
        diff_y = distance * math.sin(alpha)
        if abs(diff_x) < tiny:
            diff_x = 0
        if abs(diff_y) < tiny:
            diff_y = 0
        if (diff_x, diff_y) == (0, 0):
            continue

        new_points = []
        td_x = p2[0] - p1[0]
        td_y = p2[1] - p1[1]
        if diff_x == 0:
            it_x = float('inf')
        else:
            it_x = abs(td_x / diff_x)
        if diff_y == 0:
            it_y = float('inf')
        else:
            it_y = abs(td_y / diff_y)
        number_iterations = math.floor(min(it_x, it_y))
        for i in range(1, number_iterations):
            new_points.append((f'rep{a}_{b}-{i-1}', (p1[0] + diff_x * i, p1[1] + diff_y * i)))
        data['repeaters'] = new_points


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
        points.append((float(xy[0].replace(',', '.')), float(xy[1].replace(',', '.'))))
    return points


def stringify_points(points):
    ret = ""
    for p in points:
        ret += str(p[0]) + " " + str(p[1]) + "  "
    ret = ret.rstrip()
    return ret


def get_r_values(bb, topology):
    v = bb['small_side'] / 100
    edge_lens = []
    for n1, n2, data in topology.edges(data=True):
        edge_lens.append(int(geom.point_to_point(*data['points'])))
    edge_lens.sort()
    sf = topology.graph['scale_factor']

    r = [
        (5 * sf, 'real_world_tiny'),
        (10 * sf, 'real_world_small'),
        (20 * sf, 'real_world_med'),
        (40 * sf, 'real_world_great'),
        (60 * sf, 'real_world_severe'),
        (80 * sf, 'real_world_disastrous'),
    ]

    #for i in range(1, 6):
    #     r.append((i * 100, f'topology_{i*100}'))

    #r.append((100, f'topology_{100}'))
    #r.append((1000, f'topology_{1000}'))
    #r.append((1500, f'topology_{1500}'))
    for a in r:
        if a[0] == 0:
            r.remove(a)

    #r.sort()
    for v in range(0, len(r)):
        r[v] = int(r[v][0]), r[v][1]
    return r
