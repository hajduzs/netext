import logging
import mip
import networkx as nx
import matplotlib.pyplot as plt


class ConstraintGraph:

    def __init__(self, c: mip.ConstrList):
        self.G = nx.Graph()

        for constraint in c:
            if constraint.slack < 0.001:
                print(constraint)
                zones = [int(x.name[4:-1]) for x in constraint.expr.expr]
                name = constraint.name
                cost = -constraint.expr.const

                for z in zones:
                    self.G.add_node(z, bipartite=1)

                self.G.add_node(name, cost=cost, bipartite=0)

                self.G.add_edges_from([(z, name) for z in zones])

    def print_data(self):
        logging.debug('Constraint graph data:')
        logging.debug("LHS nodes:")
        for n, d in self.G.nodes(data=True):
            if d['bipartite'] == 0:
                logging.debug("{} <{}> : {}".format(n, [x for x in self.G.neighbors(n)],  d['cost']))
        logging.debug("RHS nodes:")
        logging.debug(f'{[n for n, d in self.G.nodes(data=True) if d["bipartite"] == 1]}')
        logging.debug(f'{self.G.edges}')

        X, Y = nx.bipartite.sets(self.G)
        pos = dict()
        pos.update((n, (2, i)) for i, n in enumerate(X))  # put nodes from X at x=1
        pos.update((n, (1, i)) for i, n in enumerate(Y))  # put nodes from Y at x=2
        nx.draw(self.G, pos=pos, with_labels=True)
        plt.show()

    def LHS(self):
        return [(n, d) for n, d in self.G.nodes(data=True) if d["bipartite"] == 0]

    def RHS(self):
        return [n for n, d in self.G.nodes(data=True) if d["bipartite"] == 1]

    def N(self, node):
        return [n for n in self.G.neighbors(node)]

    def optimize(self, CL):
        m = mip.Model()
        m.verbose = 0
        lhs = self.LHS()
        C = {}
        for i in range(0, len(lhs)):
            C[lhs[i][0]] = (m.add_var(var_type=mip.BINARY), lhs[i][1]['cost'])
        for n in self.RHS():
            m += mip.xsum([C[k][0] for k in self.N(n)]) >= 1

        m.objective = mip.minimize(mip.xsum([c * w for c, w in C.values()]))

        s = m.optimize()
        m.write("xdd.lp")

        chosen = []
        for n, v in C.items():
            if v[0].x == 1:
                i = int(n) #int(n[7:-1])
                chosen.append(CL[i] + (v[1], self.N(n)))
        return chosen

    # > mi a faszra gondoltam itt


