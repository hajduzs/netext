import networkx as nx
import matplotlib.pyplot as plt


class EdgeVertex:
    def __init__(self, edge):
        e = None
        if str(edge[0]) < str(edge[1]):
            e = edge
        else:
            e = (edge[1], edge[0])
        self.name = str(e[0]) + "/" + str(e[1])
        self.edge = e

    def __key(self):
        return self.name

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, EdgeVertex):
            return self.edge == other.edge
        return NotImplemented

    def __ne__(self, other):
        return not self == other

    def __lt__(self, other):
        if str(self.edge[0]) < str(other.edge[0]):
            return True
        elif str(self.edge[0]) == str(other.edge[0]):
            return str(self.edge[1]) < str(other.edge[1])
        return False

    def __le__(self, other):
        return self == other or self < other

    def __gt__(self, other):
        if str(self.edge[0]) > str(other.edge[0]):
            return True
        elif str(self.edge[0]) == str(other.edge[0]):
            return str(self.edge[1]) > str(other.edge[1])
        return False

    def __ge__(self, other):
        return self == other or self > other


class BipartiteDisasterGraph:

    def __init__(self, cut_list, topology):
        self.topology = topology
        self.Cuts = cut_list
        self.Edges = cut_list.return_all_protecting_edges()
        self.total_edges_left = 0
        self.graph = self.load_graph()

    def return_ids_for_cut(self, node_name):
        return self.Cuts.cutList[node_name].return_danger_zone_ids()

    def load_graph(self):
        G = nx.Graph()

        for e in self.Edges:
            G.add_node(e.name, vrtx=e, bipartite=0)
            self.total_edges_left += 1

        for c in self.Cuts:
            G.add_node(c.id, cut=c, bipartite=1, cost=float("inf"), neigh=0)

        for e in self.Edges:
            for c in self.Cuts:
                if e in c.return_protecting_edges(self.topology):
                    G.add_edge(e.name, c.id, weight=0, cost=0, valid=0, path=None)
        return G

    def return_graph(self):
        return self.graph

    def set_edge_weight(self, e, weight):
        attrs = {e: {'weight': weight}}
        nx.set_edge_attributes(self.graph, attrs)

    def set_edge_cost(self, e, cost):
        attrs = {e: {'cost': cost}}
        nx.set_edge_attributes(self.graph, attrs)

    def set_edge_path(self, e, path):
        attrs = {e: {'path': path}}
        nx.set_edge_attributes(self.graph, attrs)

    def set_edge_valid(self, e, v):
        attrs = {e: {'valid': v}}
        nx.set_edge_attributes(self.graph, attrs)

    def __str__(self):
        c = "- Bipartite Disaster Graph -\n"
        c += "nodes_left: {}\n".format([n[0] for n in self.graph.nodes(data=True) if n[1]["bipartite"]==0])
        c += "nodes_right: {}\n".format([n[0] for n in self.graph.nodes(data=True) if n[1]["bipartite"]==1])
        c += "edges: {}\n".format(self.graph.edges(data=True))
        return c

    def num_path_calls(self):
        total_n = 0
        for n, d in self.graph.nodes(data=True):
            if d['bipartite'] == 1:
                continue
            nc = [x for x in self.graph.neighbors(n)]
            # print(f'Edge {n} nc: {len(nc)}')

            total_n += 2 ** len(nc) - 1
        return total_n

    def get_neighbors_distribution(self):
        dist = dict()
        for n, d in self.graph.nodes(data=True):
            if d['bipartite'] == 0:
                nc = self.graph.degree[n]
                if nc in dist:
                    dist[nc] += 1
                else:
                    dist[nc] = 1
        dist = list(dist.items())
        dist.sort()
        return dist

    def plot(self, filepath):
        plt.close()
        left = [n[0] for n in self.graph.nodes(data=True) if n[1]['bipartite'] == 0]
        positions = nx.drawing.bipartite_layout(self.graph, left)
        colors = []
        edge_labels = dict()
        for u, v, d in self.graph.edges(data=True):
            edge_labels[(u, v)] = str(d['cost'])
            c = '#000000'
            if d['weight'] == 0 and d['valid'] == 0:
                c = '#000000'
            if d['weight'] == 0 and d['valid'] == 1:
                c = '#0000DD'
            if d['weight'] == 1 and d['valid'] == 0:
                c = '#FFA500'
            if d['weight'] == 1 and d['valid'] == 1:
                c = '#00FF00'
            colors.append(c)
        nx.draw(self.graph, with_labels=True, edge_color=colors, pos=positions)
        nx.draw_networkx_edge_labels(self.graph, pos=positions, edge_labels=edge_labels)
        plt.savefig(filepath)
        plt.close()
