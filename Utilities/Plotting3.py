import matplotlib.pyplot as plt
import networkx as nx
from shapely.geometry import Polygon
from descartes import PolygonPatch
import helper_functions as func
import json

def get_colors_form_file(n):
    file = open("../other_data/distinct_colors.txt", 'r')
    colors = file.readlines()
    file.close()
    ret = [c.rstrip() for c in colors]
    if n > 64:
        for i in range(64, n):
            ret.append(ret[i % 64])
        return ret
    else:
        return ret[:n]


def read_json_graph(jsonpath, R):
    with open(jsonpath) as f:
        data = json.load(f)

    G = nx.Graph()
    for node in data["nodes"]:
        G.add_node(node["id"], coords=node["coords"])

    for edge in data["edges"]:
        G.add_edge(edge["from"], edge["to"])

    func.append_data_with_edge_chains(G)

    return G

def replot(gname, jsonpath, zones, paths, R):
    figure, ax = plt.subplots()

    graph = read_json_graph(jsonpath, R)

    bb = func.calculateBoundingBox(graph, R)
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

    filepath = gname + ".tex"

    import tikzplotlib
    tikzplotlib.save(filepath)

    filepath = gname + ".png"
    figure.savefig(filepath, dpi=300)

'''
replot("teliasonero_eu",
       "../work/teliasonero_eu/teliasonero_eu.json",
       "../work/teliasonero_eu/r_0.28619999999999995/data/zones.txt",
       "../work/teliasonero_eu/r_0.28619999999999995/data/paths.txt",
       0.28619999999999995)
'''

import os

def replot_all():
    graphs = []
    for(dp, dn, fns) in os.walk("../output"):
        graphs = dn
        break

    for x in graphs:
        for(dp, dn, fns) in os.walk("../output/{}/".format(x)):
            lol = "{}{}/data/".format(dp, dn[0])
            replot(x, "../output/{}/{}".format(x,fns[0]), lol+"zones.txt", lol+"paths.txt", float(dn[0].split("_")[1]))
            break

replot_all()