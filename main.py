import algorithms.graph_reading
from algorithms import helper_functions as func
import Utilities.Writer as l_out
from NetworkModels.DangerZones import DangerZoneList
from NetworkModels.DisasterCuts import CutList
from NetworkModels.BipartiteGraph import BipartiteDisasterGraph
from Utilities.Plotting import plot
from libs.Wrappers.PlanarDivider import get_division_from_json
import os
import sys
import shutil
import logging

# GLOBAL VARIABLES
import math


DEBUG_MODE = True

GAMMA = 2 / math.sqrt(3)    # anything wider than 120° will be ignored
FILES = {}

# paths
if len(sys.argv) > 1 and DEBUG_MODE is False:
    FILES['input_dir'] = "graphs/" + sys.argv[1] + "/"
else:
    if os.path.exists("output"):
        shutil.rmtree("output")
    FILES['input_dir'] = "graphs/debug/"

if not os.path.exists("output"):
    os.mkdir("output")

for g in func.load_graph_names(FILES):

    func.create_output_directory(FILES, g)

    # Generate (or read, if it already exists) JSON from input file

    if func.generate_or_read_json(FILES, g) is None:
        logging.critical("Could not generate JSON")
        continue

    # Load topology, append it with data, create bounding box

    TOPOLOGY = algorithms.graph_reading.load_graph_form_json(FILES['js_name'])
    BOUNDING_BOX = func.calculate_bounding_box(TOPOLOGY)
    func.append_data_with_edge_chains(TOPOLOGY)

    R_values = [BOUNDING_BOX['small_side'] * scale / 100 for scale in range(5, 16)]
    for R in R_values[1:2]:

        func.create_r_output_directory(FILES, R)

        logging.debug(f'{R} for {FILES["g_path"]} -- source: {FILES["input_dir"]}')

        # generate danger zones, and then the bipartite disaster graph

        faces = get_division_from_json(R, FILES['js_name'], "{}/faces.txt".format(FILES['g_r_path_data']))
        if faces is None:
            print("something went awfully wrong, im sorry. (could not calculate faces properly)")
            continue
        DZL = DangerZoneList(TOPOLOGY, R, GAMMA, faces)
        l_out.write_dangerzones("{}/{}".format(FILES['g_r_path_data'], "zones.txt"), DZL)

        # TODO what if there are too many Danger zones (for ex: colt with 7500)

        logging.info(f'Danger zones in total: {len(DZL.dangerZones)}')

        if len(DZL.dangerZones) > 699:
            logging.warning("We do not continue further, as there are too many danger zones.")
            continue

        BPD = BipartiteDisasterGraph(CutList(DZL))

        # now we can choose the method

        chosen_edges = None
        switch = -1

        if switch == 0:             # Original heuristic (v2)
            from algorithms.heuristic_version_2 import heuristic_2
            heuristic_2(TOPOLOGY, DZL, BPD, R, FILES['g_r_path_data'])

        if switch == 1:             # LP only "top level" constraints
            from algorithms.LP_all_constraints import linear_prog_method
            linear_prog_method(TOPOLOGY, DZL, BPD, R, FILES['g_r_path_data'], all_constr=False)

        if switch == 2:             # LP top level start, more constr if solution does not satisfy =s
            from algorithms.LP_all_constraints import linear_prog_method
            linear_prog_method(TOPOLOGY, DZL, BPD, R, FILES['g_r_path_data'], all_constr=False, constr_it=True)

        if switch == 3:             # LP all constraints
            from algorithms.LP_all_constraints import linear_prog_method
            linear_prog_method(TOPOLOGY, DZL, BPD, R, FILES['g_r_path_data'])

        if switch == -1:
            from algorithms.heuristic_version_2 import heuristic_2
            from algorithms.LP_all_constraints import linear_prog_method
            mod = linear_prog_method(TOPOLOGY, DZL, BPD, R, FILES['g_r_path_data'], all_constr=False)
            heuristic_2(TOPOLOGY, DZL, BPD, R, FILES['g_r_path_data'], mod)
        try:
            plot(FILES)
        except:
            logging.warning("sorry, could not plot")
