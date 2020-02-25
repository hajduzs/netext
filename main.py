import helper_functions as func
import Utilities.Logging as logging
from NetworkModels.DangerZones import DangerZoneList
from NetworkModels.DisasterCuts import CutList
from NetworkModels.BipartiteGraph import BipartiteDisasterGraph
from Utilities.Plotting2 import plot_graph_all_3
from libs.Wrappers.PlanarDivider import get_division_from_json
import os
import sys
from Utilities.Logging import log

# GLOBAL VARIABLES

GAMMA = 1
FILES = {}

# paths
if len(sys.argv) > 1:
    FILES['input_dir'] = "graphs/" + sys.argv[1] + "/"
else:
    FILES['input_dir'] = "graphs/debug/"

if not os.path.exists("output"):
    os.mkdir("output")

for g in func.load_graph_names(FILES):

    func.create_output_directory(FILES, g)

    # Generate (or read, if it already exists) JSON from input file

    scale = 1
    if func.generate_or_read_json(FILES, scale, g) is None:
        log("COULD NOT GENERATE JSON")
        continue

    # Load topology, append it with data, create bounding box

    TOPOLOGY = func.load_graph_form_json(FILES['js_name'])
    BOUNDING_BOX = func.calculateBoundingBox(TOPOLOGY)
    func.append_data_with_edge_chains(TOPOLOGY)

    R_values = [BOUNDING_BOX['small_side'] * scale / 100 for scale in range(5, 16)]
    for R in R_values[1:2]:

        print("{} for {}".format(R, FILES['g_path']))

        func.create_r_output_directory(FILES, R)

        # generate danger zones, and then the bipartite disaster graph

        faces = get_division_from_json(R, FILES['js_name'], "{}/faces.txt".format(FILES['g_r_path_data']))
        if faces is None:
            print("something went awfully wrong, im sorry. (could not calculate faces properly)")
            continue
        DZL = DangerZoneList(TOPOLOGY, R, GAMMA, faces)
        logging.write_dangerzones("{}/{}".format(FILES['g_r_path_data'], "zones.txt"), DZL)
        BPD = BipartiteDisasterGraph(CutList(DZL))

        # now we can choose the method

        chosen_edges = None
        switch = 1

        if switch == 0:             # Original heuristic (v2)
            from algorithms.heuristic_version_2 import heuristic_2
            chosen_edges = heuristic_2(TOPOLOGY, DZL, BPD, R)

        if switch == 1:             # LP only "top level" constraints
            from algorithms.LP_all_constraints import linear_prog_method
            chosen_edges = linear_prog_method(TOPOLOGY, DZL, BPD, R, FILES['g_r_path_data'], all_constr=False)

        if switch == 2:             # LP top level start, more constr if solution does not satisfy =s
            from algorithms.LP_all_constraints import linear_prog_method
            chosen_edges = linear_prog_method(TOPOLOGY, DZL, BPD, R, FILES['g_r_path_data'], all_constr=False, constr_it=True)

        if switch == 3:             # LP all constraints
            from algorithms.LP_all_constraints import linear_prog_method
            chosen_edges = linear_prog_method(TOPOLOGY, DZL, BPD, R, FILES['g_r_path_data'])

        try:
            plot_graph_all_3(FILES['g_r_path'], TOPOLOGY, DZL, chosen_edges, BOUNDING_BOX, R)
        except:
            log("sorry, could not plot")