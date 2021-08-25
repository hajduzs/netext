# TODO: doc
from typing import List

from src.geometry.structures.Polygon import Polygon
from src.graphs.Topology import Topology
from src.netext.networkmodels._functions import hit_graph_with_disaster, is_valid_danger_zone
from src.netext.networkmodels.singles.dangerzone import DangerZone


class DangerZoneList:

    def __init__(self, topology: Topology, faces: List[Polygon], r: float):
        self._omit_count = 0
        self.zones = []

        for f in faces:
            remaining_graph = hit_graph_with_disaster(topology, f.repr_point(), r)
            valid, omit = is_valid_danger_zone(topology, remaining_graph, f, r)
            if valid:
                self.zones.append(DangerZone(remaining_graph, f))
            self._omit_count += omit

    def __len__(self):
        return len(self.zones)

    def __getitem__(self, item):
        return self.zones[item]

    def __iter__(self):
        return (z for z in self.zones)  # generator
