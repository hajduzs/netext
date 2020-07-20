import matplotlib.pyplot as plt
import networkx as nx
from shapely.geometry import Polygon
from descartes import PolygonPatch

import algorithms.graph_reading
from algorithms import helper_functions as func
import json
import logging
import re
import algorithms.Solver as S

logging.getLogger('matplotlib.font_manager').disabled = True


def get_colors_form_file(n):
    file = open("other_data/distinct_colors.txt", 'r')
    colors = file.readlines()
    file.close()
    ret = [c.rstrip() for c in colors]
    if n > 64:
        for i in range(64, n):
            ret.append(ret[i % 64])
        return ret
    else:
        return ret[:n]


def read_json_graph(jsonpath):
    with open(jsonpath) as f:
        data = json.load(f)

    G = nx.Graph()
    for node in data["nodes"]:
        G.add_node(node["id"], coords=node["coords"])

    for edge in data["edges"]:
        G.add_edge(edge["from"], edge["to"])

    func.append_data_with_edge_chains(G)

    return G


def convert_str_list_to_list(l: str):
    return [int(x) for x in l.strip().rstrip("]").lstrip("[").split(",")]


def get_zone_ids_for_cuts(cut_ids, cl, dl):
    z = set()
    for c in convert_str_list_to_list(cut_ids):
       z.update(convert_str_list_to_list(cl[c]))
    r = list(z)
    r.sort()
    return r


def replot(gname, grpath, jsonpath, zones, cuts, paths, R, type):
    figure, ax = plt.subplots()

    graph = read_json_graph(jsonpath)

    # set plot size
    bb = func.calculate_bounding_box(graph, R)
    ax.set_xlim((bb["x_min"] - R, bb["x_max"] + R))
    ax.set_ylim((bb["y_min"] - R, bb["y_max"] + R))

    for node, data in graph.nodes(data=True):
        c = plt.Circle(data['coords'], 0.01, color='blue')
        ax.add_artist(c)

    for n1, n2, data in graph.edges(data=True):
        for i in range(0, len(data['points']) - 1):
            p1 = data['points'][i]
            p2 = data['points'][i + 1]

            line = plt.Line2D((p1[0], p2[0]), (p1[1], p2[1]), color='black', linewidth=1)
            ax.add_artist(line)

    with open(cuts) as f:
        cutlist = [z.split(";")[1] for z in f.readlines()][1:]

    with open(zones) as f:
        zonelist = [z.split(";")[1] for z in f.readlines()][1:]

    with open(paths) as f:
        pathlist = [z.split(";") for z in f.readlines()][1:]

    cc = 0
    colors = get_colors_form_file(len(cutlist))

    for edge, path, cost, cuts in pathlist:
        # get danger zone polys and plot them
        asd = get_zone_ids_for_cuts(cuts, cutlist, zonelist)
        for dz in asd:
            zone = Polygon(func.destringify_points(zonelist[int(dz)]))
            ax.add_patch(PolygonPatch(zone, fc=colors[cc], ec=colors[cc], alpha=0.4, zorder=3))

        x_c, y_c = [], []
        for p in func.destringify_points(path):
            x_c.append(float(p[0]))
            y_c.append(float(p[1]))
        ax.plot(x_c, y_c, color=colors[cc], linewidth=0.8)

        cc += 1
        if cc == len(cutlist):
            cc = 0

    filepath = grpath + "/" + gname + type + ".tex"

    import tikzplotlib
    tikzplotlib.save(filepath)

    filepath = grpath + "/" + gname + type + ".png"
    figure.savefig(filepath, dpi=300)
    plt.close('all')


def plot(files):
    for method in S._METHODS:
        try:
            replot(files["g_path"].split("/")[-1],
                   files["g_r_path"],
                   files["js_name"],
                   files["g_r_path_data"] + "/zones.txt",
                   files["g_r_path_data"] + "/cuts.txt",
                   f'{files["g_r_path_data"]}/{method}_edges.txt',
                   float(files["g_r_path"].split("/")[-1].split("_")[-1]),
                   f'_{method}')
        except Exception as e:
            logging.warning(f'Plotting {method} edges failed. Cause: {e}')



def plot_preformatted(files):
    replot(files["g_path"],
           files["g_r_path"],
           files["js_name"],
           files["g_r_path_zone"],
           files["g_r_path_path"],
           files["r"])


def plot_dangerzone(jsonpath, zonepath, R):
    TOPOLOGY = algorithms.graph_reading.load_graph_form_json(jsonpath)
    func.append_data_with_edge_chains(TOPOLOGY)
    zones = []
    with open(zonepath) as f:
        lines = f.readlines()
        for i in range(1, len(lines)):
            p = lines[i].split(";")[1]
            zones.append(func.destringify_points(p))

    bb = func.calculate_bounding_box(TOPOLOGY, R)
    epsilon = 0

    figure, ax = plt.subplots()
    ax.set_xlim((bb["x_min"] - epsilon - R, bb["x_max"] + epsilon + R))
    ax.set_ylim((bb["y_min"] - epsilon - R, bb["y_max"] + epsilon + R))

    for node, data in TOPOLOGY.nodes(data=True):
        c = plt.Circle(data['coords'], 0.4, color='blue')
        ax.add_artist(c)

    for n1, n2, data in TOPOLOGY.edges(data=True):
        for i in range(0, len(data['points']) - 1):
            p1 = data['points'][i]
            p2 = data['points'][i + 1]

            line = plt.Line2D((p1[0], p2[0]), (p1[1], p2[1]), color='black', linewidth=0.2)
            ax.add_artist(line)

    cc = 0
    colors = get_colors_form_file(len(zones))

    for z in zones:
        zone = Polygon(z)
        ax.add_patch(PolygonPatch(zone, fc=colors[cc], ec=colors[cc], alpha=0.4, zorder=3))
        cc += 1

    filepath = "dangerzone.png"
    figure.savefig(filepath, dpi=300)