import logging
import mip
import networkx as nx


from NetworkModels.BipartiteGraph import BipartiteDisasterGraph
from NetworkModels.DangerZones import DangerZoneList


class ConstraintGraph:

    def __init__(self, b: BipartiteDisasterGraph, d: DangerZoneList):
        self.bpd = b
        self.dzl = d
        self.G = b.graph

    def LHS(self):
        return [n for n, d in self.G.nodes(data=True) if d["bipartite"] == 0]

    def RHS(self):
        return [n for n, d in self.G.nodes(data=True) if d["bipartite"] == 1]

    def N(self, node):
        return [n for n in self.G.neighbors(node)]

    def calculate_cost(self, node):
        pass

    def optimize(self, CL):
        m = mip.Model()
        lhs = self.LHS()
        rhs = self.RHS()
        C = {}     # edge -> cost of said edge
        for i in range(0, len(lhs)):
            C[lhs[i]] = (m.add_var(var_type=mip.BINARY), self.calculate_cost(lhs[i]))
        for n in self.RHS():
            m += mip.xsum([C[k][0] for k in self.N(n)]) >= 1
