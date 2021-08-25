"""This module contains the Topology class,
made for handling network graphs in the bounds of the program"""

import networkx as nx

from src.geometry.structures.Point import Point


class Topology:

    @staticmethod
    def get_topology_from_json(data):
        """Loads and returns graph from a .json structure"""

        # This bit only IF we need to generate more JSON files.
        # (Loads .json from filepath - used for debugging)
        # with open(filepath) as sourcefile:
        #     data = json.load(sourcefile)

        g = nx.Graph()
        cs = {}

        for node in data['nodes']:
            g.add_node(node['id'])
            cs[node['id']] = Point(*node['coords'])

        for edge in data['edges']:
            g.add_edge(edge['from'], edge['to'])

        # construct topology
        t = Topology()
        t.graph = g
        t.data = {
            'name': data['name'],
            'scale_factor': data['scale_factor'] if 'scale_factor' in data else 1
        }
        t.coords = cs
        return t

    def __init__(self):
        self.data: dict = dict()
        self.coords: dict = dict()
        self.graph: nx.Graph = None

