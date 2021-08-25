from typing import Set
from src.netext.networkmodels.singles.edge import EdgeVertex


class DisasterCut:

    def __init__(self, danger_zones: int, ns_a: Set[int], ns_b: Set[int]):
        self.id = None
        self.danger_zones = [danger_zones]
        self.na = ns_a
        self.nb = ns_b

    def __eq__(self, other):
        return (self.na == other.na and self.nb == other.nb) or (self.na == other.nb and self.nb == other.na)

    def join(self, other):
        self.danger_zones.extend(other.danger_zones)

    def get_protecting_edges(self):
        return [EdgeVertex(a, b) for a in self.na for b in self.nb]
