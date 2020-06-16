import networkx as nx
from NetworkModels.DisasterCuts import DisasterCut

from Utilities.HitDetection import hit_graph_with_disaster, is_face_valid_dangerzone
import shapely.geometry as geom
from algorithms.helper_functions import destringify_points, sample_point
import logging



def reset_counter():
    DangerZone.id = 0
    DisasterCut.id = 0
    DangerZoneList.omit_count = 0


class DangerZone:

    id = 0

    def __init__(self, graph, s_poly):
        self.id = DangerZone.id
        DangerZone.id += 1
        self.graph = graph
        self.string_poly = s_poly

    def get_disaster_cuts(self):
        components = [list(c) for c in nx.connected_components(self.graph)]
        cuts = []
        t = nx.number_connected_components(self.graph)
        for i in range(0, 2 ** (t - 1) - 1):
            set0 = []
            set1 = []
            set1.extend(components[-1])
            for j in range(0, (t - 1)):
                if (i >> j) % 2 == 0:
                    set0.extend(components[j])
                else:
                    set1.extend(components[j])
            cuts.append(DisasterCut(self.id, [set0, set1]))

        # wont be needing this anymore
        #del self.graph

        return cuts

    def __str__(self):
        s = "-- Danger zone --\n"
        s += "id:\t\t{}\n".format(self.id)
        s += "poly:\t\t{}\n".format(self.string_poly)
        return s


class DangerZoneList:

    def __init__(self, topology, r, gamma, faces):
        self.omit_count = 0
        self.dangerZones = []
        self.load_dangerzones(topology, r, gamma, faces)
        reset_counter()
        #log(self, "DZ_CONSTRUCTION")

    def add_danger_zone(self, dz):
        self.dangerZones.append(dz)

    def __len__(self):
        return len(self.dangerZones)

    def __getitem__(self, item):
        return self.dangerZones[item]

    def __iter__(self):
        return DZLIterator(self)

    def __str__(self):
        s = " -- DANGER ZONES -- \n"
        for dz in self.dangerZones:
            s += dz.__str__()
        return s

    def load_dangerzones(self, topology, r, gamma, faces):
        for face in faces:
            points = destringify_points(face)
            if len(points) < 3:
                continue

            poly = geom.Polygon(points)

            if poly.is_empty:  # ignore really small and degenerate polygons
                continue

            if False:
                if not poly.is_valid:
                    poly = poly.buffer(0)
                    if poly.is_empty:
                        continue

                p = poly.representative_point()
            else:
                p = sample_point(poly)

            G = hit_graph_with_disaster(topology, r, (p.x, p.y))

            if is_face_valid_dangerzone(gamma, poly, r, G, self):
                dz = DangerZone(G, face)
                self.add_danger_zone(dz)

        logging.info(f'{self.omit_count} danger zones omitted from a total od {len(faces)}')

    def generate_disaster_cuts(self):
        cuts = []
        for dz in self.dangerZones:
            cuts.extend(dz.get_disaster_cuts())
        return cuts


class DZLIterator:

    def __init__(self, dz):
        self._dz = dz
        self._index = 0

    def __next__(self):
        if self._index < len(self._dz.dangerZones):
            ret = self._dz.dangerZones[self._index]
            self._index += 1
            return ret
        raise StopIteration

