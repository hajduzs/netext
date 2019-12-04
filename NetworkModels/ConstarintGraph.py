import networkx as nx
import mip

class TreeNode:

    def __init__(self):
        self.name = None
        self.root = False
        self.parent = None
        self.children = []
        self.finished = False

    def getPath(self):
        if self.root:
            return []
        else:
            return [self.name].extend([self.parent.getPath()])


class ConstraintGraph:

    def __init__(self, c: mip.ConstrList):
        self.G = nx.Graph()

        for constraint in c:
            if constraint.slack == 0:
                print(constraint)
                zones = [int(x.name[4:-1]) for x in constraint.expr.expr]
                name = constraint.name
                cost = -constraint.expr.const

                for z in zones:
                    self.G.add_node(z, bipartite=1)

                self.G.add_node(name, cost=cost, bipartite=0)

                self.G.add_edges_from([(z, name) for z in zones])

    def print_data(self):
        print("LHS nodes: ")
        for n, d in self.G.nodes(data=True):
            if d['bipartite'] == 0:
                print("{} <{}> : {}".format(n, [x for x in self.G.neighbors(n)],  d['cost']))
        print("RHS nodes: ")
        print([n for n, d in self.G.nodes(data=True) if d['bipartite'] == 1])

    def LHS(self):
        return [(n, d) for n, d in self.G.nodes(data=True) if d["bipartite"] == 0]

    def RHS(self):
        return [n for n, d in self.G.nodes(data=True) if d["bipartite"] == 1]

    def N(self, node):
        return [n for n in self.G.neighbors(node)]

    def optimize(self, CL):
        m = mip.Model()
        lhs = self.LHS()
        C = {}
        for i in range(0, len(lhs)):
            C[lhs[i][0]] = (m.add_var(var_type=mip.BINARY), lhs[i][1]['cost'])
        for n in self.RHS():
            m += mip.xsum([C[k][0] for k in self.N(n)]) >= 1

        m.objective = mip.minimize(mip.xsum([c * w for c, w in C.values()]))

        s = m.optimize(max_seconds=60)

        chosen = []
        for n, v in C.items():
            if v[0].x == 1:
                i = int(n[7:-1])
                chosen.append(CL[i] + (v[1], self.N(n)))
        return chosen

    # > mi a faszra gondoltam itt


