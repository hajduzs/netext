from NetworkModels.DangerZones import DangerZoneList
from NetworkModels.DisasterCuts import CutList
from NetworkModels.BipartiteGraph import BipartiteDisasterGraph
from networkx import Graph
from mip import Model


class Pipeline(object):
    def __init__(self):
        self.topology: Graph = None
        self.files: dict = None
        self.r: float = None
        self.dzl: DangerZoneList = None
        self.cl: CutList = None
        self.bpd: BipartiteDisasterGraph = None
        self.lb_model: Model = None
