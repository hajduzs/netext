from NetworkModels.BipartiteGraph import EdgeVertex

def reset_counter():
    DisasterCut.id = 0


class DisasterCut:

    id = 0

    def __init__(self, danger_zones, node_sets):
        self.id = DisasterCut.id
        DisasterCut.id += 1
        self.dangerZones = [danger_zones]
        self.nodeSets = node_sets

    def __eq__(self, other):
        n1a = set(self.nodeSets[0])
        n2a = set(other.nodeSets[0])
        n1b = set(self.nodeSets[1])
        n2b = set(other.nodeSets[1])
        return (n1a == n2a and n1b == n2b) or (n1a == n2b and n1b == n2a)

    def get_name(self):
        return 'v'+str(self.id)

    def join(self, other):
        self.dangerZones.extend(other.dangerZones)

    def return_danger_zone_ids(self):
        return self.dangerZones

    def return_protecting_edges(self):
        return [EdgeVertex((a, b)) for a in self.nodeSets[0] for b in self.nodeSets[1]]

    def __str__(self):
        s = "-- Disaster Cut --\n"
        s += "id:\t\t{}\n".format(self.id)
        s += "dz ids:\t\t{}\n".format(self.dangerZones)
        s += "node sets:\t\t{} and {}\n".format(self.nodeSets[0], self.nodeSets[1])
        return s


class CutList:
    def __init__(self, DZL):
        self.cutList = []
        for cut in DZL.generate_disaster_cuts():
            self.add_disaster_cut(cut)

    def get_cut_count(self):
        return len(self.cutList)

    def add_disaster_cut(self, disaster_cut):
        for cut in self.cutList:
            if cut == disaster_cut:
                cut.join(disaster_cut)
                return
        self.cutList.append(disaster_cut)

    def return_danger_zones_for_cut(self, cut_name):
        for cut in self.cutList:
            if cut.name == cut_name:
                return cut.return_danger_zone_ids()
        return None

    def return_all_protecting_edges(self):
        vertices = set()
        for cut in self.cutList:
            vertices.update(cut.return_protecting_edges())
        l = list(vertices)
        l.sort()
        return l

    def __str__(self):
        s = "-- DISASTER CUTS --\n"
        for c in self.cutList:
            s += c.__str__()
        return s

    def __iter__(self):
        return CLIterator(self)


class CLIterator:

    def __init__(self, cl):
        self._cl = cl
        self._index = 0

    def __next__(self):
        if self._index < len(self._cl.cutList):
            ret = self._cl.cutList[self._index]
            self._index += 1
            return ret
        raise StopIteration
