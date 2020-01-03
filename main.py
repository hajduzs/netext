from datetime import datetime

import my_functions as func
from Utilities.Logging import log, set_out
from NetworkModels.DangerZones import DangerZoneList, DangerZone
from Utilities.HitDetection import is_face_valid_dangerzone, hit_graph_with_disaster
from NetworkModels.BipartiteGraph import BipartiteDisasterGraph
from NetworkModels.ConstarintGraph import ConstraintGraph
from Wrappers.PathPlanner import PathPlanner
from Utilities.Plotting2 import plot_graph_all_3, plot_graph_with_node_labels
from Utilities.Outputter import *

from Wrappers.PlanarDivider import get_division_from_json

import os
import shapely.geometry as geom
import mip
import itertools
import sys

# GLOBAL VARIABLES

GAMMA = 1

# paths

inputdir = None

if len(sys.argv) > 1:
    inputdir = "graphs/" + sys.argv[1] + "/"
else:
    inputdir = "graphs/"

graphlist = []

for (dp, dn, filenames) in os.walk(inputdir):
    graphlist.extend(filenames)
    break

if not os.path.exists("output"):
    os.mkdir("output")

for g in graphlist:

    # MAKE OUTPUT FOLDER

    gpath = "output/{}".format(g.split('.')[0])
    os.mkdir(gpath)

    # GENERATE JSON FROM LGF

    scale = 100 # just leave it there:

    js = None

    if g.split('.')[1] == "lgf":
        js = func.generate_json_from_lgf(inputdir + g, scale)

    if g.split('.')[1] == "gml":
        js = func.generate_json_from_gml(inputdir + g, scale)

    if js is None:
        print("Not supported file format for {}. continuing as if nothing happened".format(g))
        continue

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
            poly = geom.Polygon(func.destringify_points(face))

            if poly.is_empty:   # ignore really small and degenetate polygons
                continue

            if not poly.is_valid:
                poly = poly.buffer(0)
                if poly.is_empty:
                    continue

            p = poly.representative_point()

            G = hit_graph_with_disaster(TOPOLOGY, R, (p.x, p.y))

            if is_face_valid_dangerzone(GAMMA, poly, R, G):
                dz = DangerZone(G, poly, face)
                DZL.add_danger_zone(dz)

        write_dangerzones("{}/{}".format(g_r_path, "zones.txt"), DZL)

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

        MODEL = mip.Model()
        X = [MODEL.add_var(var_type=mip.CONTINUOUS) for i in range(0, len(DZL))]

        # constraintek feltoltese

        CL = {}
        c_index = 0

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

            i_subsets = itertools.chain.from_iterable(itertools.combinations(ids, r) for r in range(1, len(ids) + 1))
            for subs in i_subsets:
                PP.calculate_r_detour(pi, pg, subs)
                MODEL += mip.xsum([X[k] for k in subs]) <= PP.getCost()
                CL[c_index] = (pnodes, PP.getPath())
                c_index += 1

        MODEL.objective = mip.maximize(mip.xsum(X))

        # max egy percig fusson
        status = MODEL.optimize(max_seconds=60)

        print('solution:')
        for v in MODEL.vars:
            print('{} : {}'.format(v.name, v.x))

        CG = ConstraintGraph(MODEL.constrs)

        CG.print_data()

        chosen_edges = CG.optimize(CL)

        write_paths("{}/{}".format(g_r_path, "paths.txt"), chosen_edges)

        acsum = 0
        for edge, path, cost, zones in chosen_edges:
            acsum += cost
            lowerbound = sum([MODEL.vars[id].x for id in zones])
            print("ids: {}".format([z for z in zones]))
            print("compare done for edge {}. LB: {} AC: {} .. diff: {} (+{}%)".format(edge, lowerbound, cost,
                                                                                      cost - lowerbound,
                                                                                      100 * (cost - lowerbound) / lowerbound))

        lbsum = sum([MODEL.vars[i].x for i in range(0, len(DZL))])
        print("In total: LB: {}, AC: {} .. diff: {} (+{}%)".format(lbsum, acsum, acsum - lbsum,
                                                                   100 * (acsum - lbsum) / lbsum))

        #plot_graph_all_3(g_r_path, TOPOLOGY, DZL, chosen_edges, bb, R)