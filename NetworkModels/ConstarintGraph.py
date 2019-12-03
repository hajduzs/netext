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

    def __init__(self, c):
        self.G = nx.Graph()

        for constraint in c:
            if constraint.slack == 0:
                zones = [int(x.name[4:-1]) for x in c.expr.expr]
                name = constraint.name
                cost = -constraint.expr.cost

                for z in zones:
                    self.G.add_node(z, bipartite=1)

                self.G.add_node(name, cost=cost, bipartite=0)

                self.G.add_edges_from([(z, name) for z in zones])


    def optimize(self):
        pass
    # > mi a faszra gondoltam itt


