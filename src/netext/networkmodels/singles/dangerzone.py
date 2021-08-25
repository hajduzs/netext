# TODO: documentation
import networkx as nx

from src.geometry.structures.Polygon import Polygon
from src.netext.networkmodels.singles.disastercut import DisasterCut


class DangerZone:

    id = 0

    def __init__(self, remaining_graph: nx.Graph, polygon: Polygon):
        self.id = DangerZone.id
        DangerZone.id += 1
        self.remaining_graph = remaining_graph
        self.polygon = polygon

    def generate_cuts(self):
        components = [list(c) for c in nx.connected_components(self.remaining_graph)]
        cuts = []
        t = nx.number_connected_components(self.remaining_graph)
        for i in range(0, 2 ** (t - 1) - 1):
            set0 = []
            set1 = []
            set1.extend(components[-1])
            for j in range(0, (t - 1)):
                if (i >> j) % 2 == 0:
                    set0.extend(components[j])
                else:
                    set1.extend(components[j])
            cuts.append(DisasterCut(self.id, set(set0), set(set1)))

        del self.remaining_graph  # wont be needing this anymore

        return cuts
