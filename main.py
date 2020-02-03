import helper_functions as func
from Utilities.Logging import log, set_out
import Utilities.Logging as logging
from NetworkModels.DangerZones import DangerZoneList
from NetworkModels.BipartiteGraph import BipartiteDisasterGraph
from Utilities.Plotting2 import plot_graph_all_3


from libs.Wrappers.PlanarDivider import get_division_from_json
import os
import sys

# TODO for later: add generator functions with 'yield' for optimisation

# GLOBAL VARIABLES

GAMMA = 1
FILES = {}

# paths

FILES['input_dir'] = None

if len(sys.argv) > 1:
    FILES['input_dir'] = "graphs/" + sys.argv[1] + "/"
else:
    FILES['input_dir'] = "graphs/debug/"

graphlist = []

for (dp, dn, filenames) in os.walk(FILES['input_dir']):
    graphlist.extend(filenames)
    break

if not os.path.exists("output"):
    os.mkdir("output")

for g in graphlist:

    # MAKE OUTPUT FOLDER

    FILES['g_path'] = "output/{}".format(g.split('.')[0])     # gpath = output/test
    if not os.path.exists(FILES['g_path']):
        os.mkdir(FILES['g_path'])

    # GENERATE JSON FROM LGF

    scale = 1

    js = None

    if g.split('.')[1] == "lgf":
        js = func.generate_json_from_lgf(FILES['input_dir'] + g, scale)

    if g.split('.')[1] == "gml":
        js = func.generate_json_from_gml(FILES['input_dir'] + g, scale)

    if js is None:
        print("Not supported file format for {}. continuing as if nothing happened".format(g))
        continue

    FILES['js_name'] = FILES['g_path'] + "/" + g.split(".")[0] + ".json"        # jsname = output/test/test.json
    if not os.path.exists(FILES['js_name']):
        with open(FILES['js_name'], "w") as f:
            f.write(js)

    # LOAD TOPOLOGY AND APPEND IT WITH DATA

    TOPOLOGY = func.load_graph_form_json(FILES['js_name'])
    bb = func.calculateBoundingBox(TOPOLOGY)

    func.append_data_with_edge_chains(TOPOLOGY)
    #plot_graph_with_node_labels(gpath + "/labels.jpg", TOPOLOGY)

    # CALCULATE FEASIBLE R VALUES

    small_side = min(bb["x_max"] - bb["x_min"], bb["y_max"] - bb["y_min"])

    R_values = [small_side * scale / 100 for scale in range(5, 16)]

    for R in R_values[3:4]:
        FILES['g_r_path'] = FILES['g_path'] + "/r_{}".format(R)        # g_r_path = output/test/r_10
        os.mkdir(FILES['g_r_path'])

        FILES['g_r_path_data'] = FILES['g_r_path'] + "/data"
        os.mkdir(FILES['g_r_path_data'])

        set_out(FILES['g_r_path'] + "/log.txt")              # output/test/r_10/log.txt

        # GENERATE DANGER ZONES

        DZL = DangerZoneList(TOPOLOGY, R, GAMMA, get_division_from_json(R, FILES['js_name'], "{}/faces.txt".format(FILES['g_r_path_data'])))
        logging.write_dangerzones("{}/{}".format(FILES['g_r_path_data'], "zones.txt"), DZL)

        log(DZL, "DZ_CONSTRUCTION")

        # GENERATE CUTS FROM DANGER ZONES

        CL = DZL.generate_disaster_cuts()
        log(CL, "CUT_CONSTRUCTION")

        # CONSTRUCT THE BIPARTITE DISASTER GRAPH

        BPD = BipartiteDisasterGraph(CL)
        log(BPD, "BIPARTITE_CONSTRUCTION")

        # now we can choose the method

        switch = False

        if switch:
            pass

        if True:
            from algorithms.LP_all_constraints import lp_all_constraints
            chosen_edges = lp_all_constraints(TOPOLOGY, DZL, BPD, R, FILES['g_r_path_data'])
            plot_graph_all_3(FILES['g_r_path'], TOPOLOGY, DZL, chosen_edges, bb, R)

        print("done")
