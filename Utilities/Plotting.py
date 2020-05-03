import matplotlib.pyplot as plt
import networkx as nx
from shapely.geometry import Polygon
from descartes import PolygonPatch

import algorithms.graph_reading
from algorithms import helper_functions as func
import json
import logging

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


def replot(gname, grpath, jsonpath, zones, paths, R, type):
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

            line = plt.Line2D((p1[0], p2[0]), (p1[1], p2[1]), color='black', linewidth=0.2)
            ax.add_artist(line)

    with open(zones) as f:
        zonelist = [z.split(";")[1] for z in f.readlines()][1:]

    with open(paths) as f:
        pathlist = [z.split(";") for z in f.readlines()][1:]

    cc = 0
    colors = get_colors_form_file(len(zonelist))

    for edge, path, cost, zones in pathlist:
        # get danger zone polys and plot them
        for dz in zones.strip().rstrip("]").lstrip("[").split(","):
            zone = Polygon(func.destringify_points(zonelist[int(dz)]))
            ax.add_patch(PolygonPatch(zone, fc=colors[cc], ec=colors[cc], alpha=0.4, zorder=3))

        spoints = path.split('  ')
        points = [(p.split(' ')) for p in spoints]
        for i in range(0, len(points) - 1):
            p1 = (float(points[i][0]), float(points[i][1]))
            p2 = (float(points[i + 1][0]), float(points[i + 1][1]))

            line = plt.Line2D((p1[0], p2[0]), (p1[1], p2[1]), color=colors[cc], linewidth=0.5 * 1.5)
            ax.add_artist(line)
        cc += 1
        if cc == len(zones):
            cc = 0

    filepath = grpath + "/" + gname + type + ".tex"

    import tikzplotlib
    tikzplotlib.save(filepath)

    filepath = grpath + "/" + gname + type + ".png"
    figure.savefig(filepath, dpi=300)


def plot(files):
    replot(files["g_path"].split("/")[-1],
           files["g_r_path"],
           files["js_name"],
           files["g_r_path_data"] + "/zones.txt",
           files["g_r_path_data"] + "/lp_paths.txt",
           float(files["g_r_path"].split("/")[-1].split("_")[-1]),
           "_lp")
    replot(files["g_path"].split("/")[-1],
           files["g_r_path"],
           files["js_name"],
           files["g_r_path_data"] + "/zones.txt",
           files["g_r_path_data"] + "/heur_paths.txt",
           float(files["g_r_path"].split("/")[-1].split("_")[-1]),
           "_heur")


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