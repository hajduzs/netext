from datetime import datetime

import my_functions as func
from Utilities.Logging import log, set_out
from NetworkModels.DangerZones import DangerZoneList, DangerZone, reset_counter
from Utilities.HitDetection import is_face_valid_dangerzone, hit_graph_with_disaster
from NetworkModels.BipartiteGraph import BipartiteDisasterGraph
from Wrappers.PathPlanner import PathPlanner
from Utilities.Plotting2 import plot_graph_all_2, plot_graph_with_node_labels

import Utilities.Geometry2D as CustomGeom
from Wrappers.PlanarDivider import get_division_from_json

import json
import os
import shapely.geometry as geom
import networkx as nx
import mip
import itertools

# GLOBAL VARIABLES

GAMMA = 1.07

# paths

graphlist = []

for (dp, dn, filenames) in os.walk("graphs/"):
    graphlist.extend(filenames)
    break

if not os.path.exists("output"):
    os.mkdir("output")

now = datetime.now().strftime('%Y%m%d-%H%M%S')
os.mkdir("output/{}".format(now))

for g in graphlist:

    # MAKE OUTPUT FOLDER

    gpath = "output/{}/{}".format(now, g.split('.')[0])
    os.mkdir(gpath)      # We don't need to check if it already exists, because filenames are unique.

    # GENERATE JSON FROM LGF

    js = func.generate_json_from_lgf("graphs/"+g)
    jsname = gpath + "/" + g.split(".")[0] + ".json"
    with open(jsname, "w") as f:
        f.write(js)

    # LOAD TOPOLOGY AND APPEND IT WITH DATA

    TOPOLOGY = func.load_graph_form_json(jsname)
    bb = func.calculateBoundingBox(TOPOLOGY)

    func.append_data_with_edge_chains(TOPOLOGY)
    plot_graph_with_node_labels(gpath + "/labels.jpg", TOPOLOGY)

    # CALCULATE FEASIBLE R VALUES

    small_side = min(bb["x_max"] - bb["x_min"], bb["y_max"] - bb["y_min"])

    R_values = [small_side * scale / 100 for scale in range(5, 16)]

    for R in R_values[3:4]:
        g_r_path = gpath + "/r{}".format(R)
        os.mkdir(g_r_path)
        set_out(g_r_path + "/log.txt")

        # GENERATE DANGER ZONES

        DZL = DangerZoneList()

        for face in get_division_from_json(R, jsname, "{}/faces.txt".format(g_r_path)):
            #try:
            poly = geom.Polygon(func.destringify_points(face))

            if not poly.is_valid:
                poly = poly.buffer(0)

            p = poly.representative_point()

            G = hit_graph_with_disaster(TOPOLOGY, R, (p.x, p.y))

            if is_face_valid_dangerzone(GAMMA, poly, R, G):
                dz = DangerZone(G, poly, face)
                DZL.add_danger_zone(dz)

            #except Exception as e:
                #log("### EXCEPTION ####\n", "DZ_CONSTRUCTION")
                #log(repr(e), "DZ_CONSTRUCTION")
                #log("\nface:\n{}\n".format(face), "DZ_CONSTRUCTION")

        log(DZL, "DZ_CONSTRUCTION")

        # GENERATE CUTS FROM DANGER ZONES

        CL = DZL.generate_disaster_cuts()
        log(CL, "CUT_CONSTRUCTION")

        # CONSTRUCT THE BIPARTITE DISASTER GRAPH

        BPD = BipartiteDisasterGraph(CL)
        log(BPD, "BIPARTITE_CONSTRUCTION")

        # SET UP PATH PLANNER

        PP = PathPlanner()
        PP.setR(R)

        # load danger zones into the path planner
        for dz in DZL:
            PP.addDangerZone(dz.string_poly)

        # TODO:
        # LP problem

        # Model 1 with every constraint

        MODEL = mip.Model()
        X = [MODEL.add_var(var_type=mip.CONTINUOUS) for i in range(0, len(DZL))]

        # constraintek feltöltése

        for n, d in BPD.graph.nodes(data=True):
            if d["bipartite"] == 1: continue

            # get ccordinates
            pnodes = d["vrtx"].edge
            pi = func.get_coords_for_node(pnodes[0], TOPOLOGY)
            pg = func.get_coords_for_node(pnodes[1], TOPOLOGY)

            # get adjacent danger zones
            neigh_cuts = [v for v in BPD.graph.nodes if BPD.graph.has_edge(n, v)]
            d["neigh"] = len(neigh_cuts)
            ids = set()
            for c in neigh_cuts:
                ids.update(BPD.return_ids_for_cut(c))
            ids = list(ids)

            i_subsets = itertools.chain.from_iterable(itertools.combinations(ids, r) for r in range(1, len(ids)+1))
            for subs in i_subsets:
                PP.calculate_r_detour(pi, pg, subs)
                MODEL += mip.xsum([X[k] for k in subs]) <= PP.getCost()

        MODEL.objective = mip.maximize(mip.xsum(X))

        # max egy percig fusson
        status = MODEL.optimize(max_seconds=60)

        print('solution:')
        for v in MODEL.vars:
            print('{} : {}'.format(v.name, v.x))




        

