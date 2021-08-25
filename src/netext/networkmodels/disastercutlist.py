from src.netext.networkmodels.dangerzonelist import DangerZoneList
from src.netext.networkmodels.singles.disastercut import DisasterCut
from src.graphs.Topology import Topology
from typing import List


class DisasterCutList:

    def __init__(self, zone_list: DangerZoneList, topology: Topology):
        self.cuts: List[DisasterCut] = []
        for z in zone_list:
            for c in z.generate_cuts():
                self._add_disaster_cut(c)
        for i in range(0, len(self.cuts)):
            self.cuts[i].id = i

    def __len__(self):
        return len(self.cuts)

    def __iter__(self):
        return (c for c in self.cuts)

    def __getitem__(self, item):
        return self.cuts[item]

    def _add_disaster_cut(self, c: DisasterCut):
        for cut in self.cuts:
            if c == cut:
                cut.join(c)
                return
        self.cuts.append(c)

    def get_all_protecting_edges(self):
        edges = set()
        for c in self.cuts:
            edges.update(c.get_protecting_edges())
        return edges


