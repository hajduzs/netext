from src.graphs.Topology import Topology
from src.netext.networkmodels.bipartitedisastergraph import BipartiteDisasterGraph
from src.netext.networkmodels.dangerzonelist import DangerZoneList
from src.netext.networkmodels.disastercutlist import DisasterCutList


class Pipeline(object):
    def __init__(self):
        self.topology: Topology = None
        self.r: float = None
        self.dzl: DangerZoneList = None
        self.cl: DisasterCutList = None
        self.bpd: BipartiteDisasterGraph = None
