import algorithms.graph_reading
from algorithms import helper_functions as func
from algorithms.algoritmhs_helper_functions import compare_chosen
import Utilities.Writer as l_out
from NetworkModels.DangerZones import DangerZoneList
from NetworkModels.DisasterCuts import CutList
from NetworkModels.BipartiteGraph import BipartiteDisasterGraph
from Utilities.Plotting import plot
from libs.Wrappers.PlanarDividerOld import get_division_from_json
import os
import sys
import shutil
import logging

# GLOBAL VARIABLES

DEBUG_MODE = False

GAMMA = 1.1    # anything wider than 120° will be ignored TODO: function to convert degrees to gamma
FILES = {}


# paths
if len(sys.argv) > 1 and DEBUG_MODE is False:
    FILES['input_dir'] = sys.argv[1] + "/"
else:
    if os.path.exists("output"):
        shutil.rmtree("output")
    FILES['input_dir'] = "graphs/tests/"

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

    for R in func.get_r_values(BOUNDING_BOX, TOPOLOGY):

        func.create_r_output_directory(FILES, R)

        logging.debug(f'{R} for {FILES["g_path"]} -- source: {FILES["input_dir"]}')

        # generate danger zones, and then the bipartite disaster graph

        faces = get_division_from_json(R, FILES['js_name'], "{}/faces.txt".format(FILES['g_r_path_data']))
        if faces is None:
            logging.critical("Could not calculate faces - continuing.")
            continue
        DZL = DangerZoneList(TOPOLOGY, R, GAMMA, faces)
        l_out.write_dangerzones("{}/{}".format(FILES['g_r_path_data'], "zones.txt"), DZL)

        logging.info(f'Danger zones in total: {len(DZL.dangerZones)}')

        if len(DZL.dangerZones) > 699:
            logging.warning("We do not continue further, as there are too many danger zones.")
            continue

        # func.append_topology_with_repeaters(TOPOLOGY, 10)

        CL = CutList(DZL, TOPOLOGY)

        l_out.write_cuts(f'{FILES["g_r_path_data"]}/cuts.txt', CL)

        BPD = BipartiteDisasterGraph(CL, TOPOLOGY)

        # now we can choose the method

        chosen_edges = None
        switch = -1

        R -= R * 0.09   # TODO: we cheat because path finding is buggy

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
            mod, pp, lp_edges = linear_prog_method(TOPOLOGY, DZL, CL, BPD, R, FILES['g_r_path_data'], all_constr=True)
            compare_chosen(lp_edges, TOPOLOGY, R, "LP")
            logging.info("-")
            he_edges = heuristic_2(TOPOLOGY, DZL, CL, BPD, R, FILES['g_r_path_data'], pp, mod)
            compare_chosen(he_edges, TOPOLOGY, R, "HEUR")

        try:
            plot(FILES)
        except:
            logging.warning("sorry, could not plot")
