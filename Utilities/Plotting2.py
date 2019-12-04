import matplotlib.pyplot as plt
import networkx as nx
from descartes import PolygonPatch


def get_colors_form_file(n):
    file = open("other_data/distinct_colors.txt", 'r')
    ret = [file.readline().rstrip() for i in range(0, n)]
    file.close()
    return ret

def plot_graph_with_node_labels(fp, graph):
    plt.close()
    nx.draw(graph, nx.get_node_attributes(graph, 'coords'), with_labels=True)
    plt.savefig(fp)
    plt.close()


def plot_graph_all(fp, graph, DZL, CL, BPD, bb, R, epsilon=0, nodesize=1, linew=0.5):
    figure, ax = plt.subplots()
    ax.set_xlim((bb["x_min"] - epsilon- R, bb["x_max"] + epsilon+R))
    ax.set_ylim((bb["y_min"] - epsilon-R, bb["y_max"] + epsilon+R))

    # Plot the original graph

    for node, data in graph.nodes(data=True):
        c = plt.Circle(data['coords'], nodesize, color='blue')
        ax.add_artist(c)

    for n1, n2, data in graph.edges(data=True):
        for i in range(0, len(data['points']) - 1):
            p1 = data['points'][i]
            p2 = data['points'][i + 1]

            line = plt.Line2D((p1[0], p2[0]), (p1[1], p2[1]), color='black', linewidth=linew)
            ax.add_artist(line)

    cc = 0
    colors = get_colors_form_file(len(DZL.dangerZones))

    # Get Valid edges. (e[0] is the edge, e[1] is the cut)
    valid = [e for e in BPD.graph.edges(data=True) if e[2]['valid'] == 1]

    for edge in valid:
        #get all cuts neighbouring e[0]
        neigh_cuts = [v for v in BPD.graph.nodes if BPD.graph.has_edge(edge[0], v)]
        #get all danger zones (they are the zones protected by the edge)
        dz_ids = set()
        for n in neigh_cuts:
            dz_ids.update(CL.return_danger_zones_for_cut(n))
        dz_ids = list(dz_ids)
        #get danger zone polys and plot them
        for id in dz_ids:
            zone = DZL.dangerZones[id].polygon
            ax.add_patch(PolygonPatch(zone, fc=colors[cc], ec=colors[cc], alpha=0.4, zorder=3))
        #plot line witch color a

        path = edge[2]['path']

        spoints = path.split('  ')
        points = [(p.split(' ')) for p in spoints]
        for i in range(0, len(points) - 1):
            p1 = (float(points[i][0]), float(points[i][1]))
            p2 = (float(points[i + 1][0]), float(points[i + 1][1]))

            line = plt.Line2D((p1[0], p2[0]), (p1[1], p2[1]), color=colors[cc], linewidth=linew * 1.5)
            ax.add_artist(line)
        cc+=1
        if(cc == len(DZL.dangerZones)):
            cc = 0

    # Save to file

    filepath = fp + "/" + graph.graph['name'] + ".jpg"
    figure.savefig(filepath, dpi=300)
    plt.clf()


def plot_graph_all_2(fp, graph, DZL, CL, BPD, bb, R, epsilon=0, nodesize=1, linew=0.5):
    figure, ax = plt.subplots()
    ax.set_xlim((bb["x_min"] - epsilon- R, bb["x_max"] + epsilon+R))
    ax.set_ylim((bb["y_min"] - epsilon-R, bb["y_max"] + epsilon+R))

    # Plot the original graph

    for node, data in graph.nodes(data=True):
        c = plt.Circle(data['coords'], nodesize, color='blue')
        ax.add_artist(c)

    for n1, n2, data in graph.edges(data=True):
        for i in range(0, len(data['points']) - 1):
            p1 = data['points'][i]
            p2 = data['points'][i + 1]

            line = plt.Line2D((p1[0], p2[0]), (p1[1], p2[1]), color='black', linewidth=linew)
            ax.add_artist(line)

    cc = 0
    colors = get_colors_form_file(len(DZL.dangerZones))

    for n, d in BPD.graph.nodes(data=True):
        #get danger zone polys and plot them
        for id in d["ids"]:
            zone = DZL.dangerZones[id].polygon
            ax.add_patch(PolygonPatch(zone, fc=colors[cc], ec=colors[cc], alpha=0.4, zorder=3))
        #plot line witch color a

        path = d['path']

        spoints = path.split('  ')
        points = [(p.split(' ')) for p in spoints]
        for i in range(0, len(points) - 1):
            p1 = (float(points[i][0]), float(points[i][1]))
            p2 = (float(points[i + 1][0]), float(points[i + 1][1]))

            line = plt.Line2D((p1[0], p2[0]), (p1[1], p2[1]), color=colors[cc], linewidth=linew * 1.5)
            ax.add_artist(line)
        cc+=1
        if(cc == len(DZL.dangerZones)):
            cc = 0

    # Save to file

    filepath = fp + "/" + graph.graph['name'] + ".jpg"
    figure.savefig(filepath, dpi=300)


def plot_graph_all_3(fp, graph, DZL, chosen, bb, R, epsilon=0, nodesize=1, linew=0.5):
    figure, ax = plt.subplots()
    ax.set_xlim((bb["x_min"] - epsilon - R, bb["x_max"] + epsilon + R))
    ax.set_ylim((bb["y_min"] - epsilon - R, bb["y_max"] + epsilon + R))

    # Plot the original graph

    for node, data in graph.nodes(data=True):
        c = plt.Circle(data['coords'], nodesize, color='blue')
        ax.add_artist(c)

    for n1, n2, data in graph.edges(data=True):
        for i in range(0, len(data['points']) - 1):
            p1 = data['points'][i]
            p2 = data['points'][i + 1]

            line = plt.Line2D((p1[0], p2[0]), (p1[1], p2[1]), color='black', linewidth=linew)
            ax.add_artist(line)

    cc = 0
    colors = get_colors_form_file(len(DZL.dangerZones))

    # plot zones and paths

    for edge, path, cost, zones in chosen:
        # get danger zone polys and plot them
        for id in zones:
            zone = DZL.dangerZones[id].polygon
            ax.add_patch(PolygonPatch(zone, fc=colors[cc], ec=colors[cc], alpha=0.4, zorder=3))

        spoints = path.split('  ')
        points = [(p.split(' ')) for p in spoints]
        for i in range(0, len(points) - 1):
            p1 = (float(points[i][0]), float(points[i][1]))
            p2 = (float(points[i + 1][0]), float(points[i + 1][1]))

            line = plt.Line2D((p1[0], p2[0]), (p1[1], p2[1]), color=colors[cc], linewidth=linew * 1.5)
            ax.add_artist(line)
        cc += 1
        if (cc == len(DZL.dangerZones)):
            cc = 0

    filepath = fp + "/" + graph.graph['name'] + ".jpg"
    figure.savefig(filepath, dpi=300)