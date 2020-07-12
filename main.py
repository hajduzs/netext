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
from Utilities.Timeit import Timeit
import os
import sys
import shutil
import logging


# GLOBAL VARIABLES
DEBUG_MODE = False
GAMMA = 1.1    # anything wider than 120° will be ignored TODO: function to convert degrees to gamma
FILES = {}

# get graph paths for the run
if len(sys.argv) > 1 and DEBUG_MODE is False:
    FILES['input_dir'] = sys.argv[1] + "/"
else:
    if os.path.exists("output"):
        shutil.rmtree("output")
    FILES['input_dir'] = "graphs/tests/"

if not os.path.exists("output"):
    os.mkdir("output")

Timeit.init()

for g in func.load_graph_names(FILES):

    # Create overall output directory for a specific graph

    func.create_output_directory(FILES, g)

    # Generate (or read, if it already exists) JSON from input file
    if func.generate_or_read_json(FILES, g) is None:
        logging.critical("Could not generate JSON")
        continue
    Timeit.time('json_generation')

    # Load topology, append it with data, create bounding box
    TOPOLOGY = algorithms.graph_reading.load_graph_form_json(FILES['js_name'])

    '''
    import matplotlib.pyplot as plt
    import networkx as nx
    print(TOPOLOGY.name)
    nx.draw_networkx(TOPOLOGY, {n:d['coords'] for n, d in TOPOLOGY.nodes(data=True)}, with_labels=True)
    plt.show()
    continue
    '''

    BOUNDING_BOX = func.calculate_bounding_box(TOPOLOGY)
    func.append_data_with_edge_chains(TOPOLOGY)

    # Write topology specific info to XML file
    write_topology_info(TOPOLOGY, FILES)

    # get feasible-looking values for R and run the algorithms
    rv = func.get_r_values(BOUNDING_BOX, TOPOLOGY)
    for R, r_comment in rv:

        print(f'{g} for {R}. {r_comment}')

        Info.get_instance().radius = R
        Info.get_instance().r_info = r_comment
        Info.get_instance().gamma = GAMMA
        Info.get_instance().success = False
        Info.get_instance().error = False
        Info.get_instance().time = dict()
        # create r-specific output directory for files
        func.create_r_output_directory(FILES, R)
        logging.debug(f'{R} for {FILES["g_path"]} -- source: {FILES["input_dir"]}')

        # Create a division of the 2D plane using the topology information
        Timeit.init('start')
        faces = get_division_from_json(R, FILES['js_name'], "{}/faces.txt".format(FILES['g_r_path_data']))
        if faces is None:
            logging.critical("Could not calculate faces - continuing.")
            continue
        Info.get_instance().num_faces = len(faces)
        Info.get_instance().time['faces'] = Timeit.time('faces_calculated')

        # Select the by-definition danger zones from the faces and create a DZ list
        DZL = DangerZoneList(TOPOLOGY, R, GAMMA, faces)
        Info.get_instance().time['zones'] = Timeit.time('dzs_calculated')
        l_out.write_dangerzones("{}/{}".format(FILES['g_r_path_data'], "zones.txt"), DZL)
        logging.info(f'Danger zones in total: {len(DZL)}')
        Info.get_instance().num_zones_omitted = DZL.omit_count
        Info.get_instance().num_zones_remaining = len(DZL)

        # If there are too many danger zones, we nope out
        if len(DZL) > 599:
            logging.warning("We do not continue further, as there are too many danger zones.")
            Info.write_run_info(FILES)
            Info.reset()
            continue
        Info.get_instance().danger_zone_component_distribution = DZL.get_distribution()

        # OPTIONAL: repeater method
        # func.append_topology_with_repeaters(TOPOLOGY, 10)

        # Generate disaster cuts from danger zones and create a Cut List
        Timeit.init()
        CL = CutList(DZL, TOPOLOGY)
        Info.get_instance().time['cuts'] = Timeit.time("cl_calculated")
        Info.get_instance().num_cuts = len(CL)
        Info.get_instance().cut_join_count = CutList.join_count
        l_out.write_cuts(f'{FILES["g_r_path_data"]}/cuts.txt', CL)

        # Create the Bipartite Disaster graph from the Information in the Cut List
        Timeit.init()
        BPD = BipartiteDisasterGraph(CL, TOPOLOGY)
        Info.get_instance().time['bpdg'] = Timeit.time('bpd_calculated')
        Info.get_instance().bpdg_neighbors_distribution = BPD.get_neighbors_distribution()
        Info.get_instance().total_constraints = BPD.num_path_calls()
        Info.get_instance().top_level_constraints = BPD.total_edges_left

        # If there are too much shortest path calculations, we just nope out
        # TODO: optimize on path calls (order them, omit some, etc)
        full = True
        if BPD.num_path_calls() > 99999:
            logging.warning("full LP too complicated. easing constraints")
            full = False

        # TODO: we cheat because path finding is buggy
        R -= R * 0.09

        try:

            mod, pp, lp_edges = linear_prog_method(TOPOLOGY, DZL, CL, BPD, R, FILES['g_r_path_data'], full=full)
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
        except Exception as e:
            logging.warning(e)
            logging.warning("sorry, could not plot")
