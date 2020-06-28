import algorithms.graph_reading
from Utilities.Data import write_topology_info
from algorithms import helper_functions as func
from algorithms.algoritmhs_helper_functions import compare_chosen
import Utilities.Writer as l_out
from NetworkModels.DangerZones import DangerZoneList
from NetworkModels.DisasterCuts import CutList
from NetworkModels.BipartiteGraph import BipartiteDisasterGraph
from Utilities.Plotting import plot
from libs.Wrappers.PlanarDividerOld import get_division_from_json
from Utilities.Data import Info
from algorithms.heuristic_version_2 import heuristic_2
from algorithms.LP_all_constraints import linear_prog_method

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

    write_topology_info(TOPOLOGY, FILES)

    rv = func.get_r_values(BOUNDING_BOX, TOPOLOGY)
    for R in rv:

        Info.get_instance().r = R
        Info.get_instance().gamma = GAMMA
        Info.get_instance().success = False

        func.create_r_output_directory(FILES, R)

        logging.debug(f'{R} for {FILES["g_path"]} -- source: {FILES["input_dir"]}')

        # generate danger zones, and then the bipartite disaster graph

        faces = get_division_from_json(R, FILES['js_name'], "{}/faces.txt".format(FILES['g_r_path_data']))
        Info.get_instance().num_faces = len(faces)
        if faces is None:
            logging.critical("Could not calculate faces - continuing.")
            continue
        DZL = DangerZoneList(TOPOLOGY, R, GAMMA, faces)
        l_out.write_dangerzones("{}/{}".format(FILES['g_r_path_data'], "zones.txt"), DZL)

        logging.info(f'Danger zones in total: {len(DZL)}')

        Info.get_instance().num_zones_omitted = DZL.omit_count
        Info.get_instance().num_zones_remaining = len(DZL)
        if len(DZL) > 599:
            logging.warning("We do not continue further, as there are too many danger zones.")
            Info.write_run_info(FILES)
            Info.reset()
            continue

        # func.append_topology_with_repeaters(TOPOLOGY, 10)

        Info.get_instance().danger_zone_component_distribution = DZL.get_distribution()

        CL = CutList(DZL, TOPOLOGY)

        Info.get_instance().num_cuts = len(CL)
        Info.get_instance().cut_join_count = CutList.join_count

        l_out.write_cuts(f'{FILES["g_r_path_data"]}/cuts.txt', CL)

        BPD = BipartiteDisasterGraph(CL, TOPOLOGY)

        Info.get_instance().bpdg_neighbors_distribution = BPD.get_neighbors_distribution()
        Info.get_instance().total_constraints = BPD.num_path_calls()
        Info.get_instance().top_level_constraints = BPD.total_edges_left

        if BPD.num_path_calls() > 99999:
            logging.warning("We do not continue further, as there are too many constraints.")
            Info.write_run_info(FILES)
            Info.reset()
            continue

        # now we can choose the method

        chosen_edges = None

        R -= R * 0.09   # TODO: we cheat because path finding is buggy

        try:
            mod, pp, lp_edges = linear_prog_method(TOPOLOGY, DZL, CL, BPD, R, FILES['g_r_path_data'])
            compare_chosen(lp_edges, TOPOLOGY, R, "LP")
            logging.info("-")
            he_edges = heuristic_2(TOPOLOGY, DZL, CL, BPD, R, FILES['g_r_path_data'], pp, mod)
            compare_chosen(he_edges, TOPOLOGY, R, "HEUR")
            Info.get_instance().success = True

        except Exception as e:
            logging.critical(e)
            logging.critical("Something went terribly wrong, im sorry.")
            Info.reset()

        Info.write_run_info(FILES)

        try:
            plot(FILES)
        except:
            logging.warning("sorry, could not plot")
