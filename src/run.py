"""
Module containing the method handling a single topology-r config run.
"""
# TODO: set up maximum number of zones, faces, etc

from src.graphs.JsonGraphGenerator import JsonGraphGenerator
from src.graphs.Topology import Topology
from src.netext.Pipeline import Pipeline
from src.netext.networkmodels.dangerzonelist import DangerZoneList
from src.netext.networkmodels.disastercutlist import DisasterCutList
from src.netext.networkmodels.bipartitedisastergraph import BipartiteDisasterGraph
from src.geometry.partition.part import get_division_from_json
from src.netext.solver.solver import Solver


def run(input_file, r, methods=None):
    pipe = Pipeline()
    pipe.r = r * 0.98

    # 0. get relevant data from input file
    js = JsonGraphGenerator(input_file).gen_json(auto_convert=True)

    # 1. Construct topology
    pipe.topology = Topology.get_topology_from_json(js)

    # 2. Generate partition using the JSON file and the specified r
    # faces MUST be a list of polygons
    faces = get_division_from_json(r, js_dump=js)

    # 3. Identify Danger Zones, Construct the Danger Zone List
    pipe.dzl = DangerZoneList(pipe.topology, faces, r)

    # 4. Construct the cuts from the danger zones
    pipe.cl = DisasterCutList(pipe.dzl, pipe.topology)

    # 5. Construct the bipartite disaster graph using the specified info.
    pipe.bpd = BipartiteDisasterGraph(pipe.cl)

    # 6. Set up solvers, solve, and save / log results
    for s in (Solver(m, pipe) for m in methods):
        try:
            s.solve()
            for e in s.solution():
                print(e)
        except:
            raise

    # TODO: run info and so on
