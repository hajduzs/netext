import networkx as nx
from src.netext.networkmodels.disastercutlist import DisasterCutList


class BipartiteDisasterGraph:

    def __init__(self, cl: DisasterCutList):
        self.cut_list = cl
        self.edge_set = cl.get_all_protecting_edges()

        self._total_calls = 0

        g = nx.Graph()
        for e in self.edge_set:
            g.add_node(e.name, bipartite=0)
        for c in self.cut_list:
            g.add_node(c.id, bipartite=1)
            protecting = c.get_protecting_edges()
            self._total_calls += 2 ** len(protecting) - 1
            for pe in protecting:
                g.add_edge(c.id, pe.name)

        self.graph = g

    def init_attributes(self):
        for n, d in self.graph.nodes(data=True):
            if d['bipartite'] == 1:
                d['cost'] = float('inf')
                d['neigh'] = 0.5
        for u, v, d in self.graph.edges(data=True):
            d['weight'] = 0
            d['cost'] = 0
            d['valid'] = 0
            d['path'] = None

    def num_path_calls(self):
        return self._total_calls

    def return_ids_for_cut(self, node_name):
        return self.cut_list[node_name].danger_zones
