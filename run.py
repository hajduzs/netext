from algorithms.algoritmhs_helper_functions import check_new_edges_bounds
import Utilities.Writer as l_out
from NetworkModels.DangerZones import DangerZoneList
from NetworkModels.DisasterCuts import CutList
from NetworkModels.BipartiteGraph import BipartiteDisasterGraph
from Utilities.Plotting import plot
from libs.Wrappers.PlanarDividerOld import get_division_from_json
from Utilities.Data import Info
#from algorithms.heuristic_version_2 import heuristic_2
# from algorithms.LP_all_constraints import linear_prog_method
from Utilities.Timeit import Timeit
from algorithms import helper_functions as func
import logging
from algorithms.Pipeline import Pipeline
import algorithms.Solver as S


def run(TOPOLOGY, GAMMA, FILES, R, r_comment, g):
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
        return None
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
        return None
    # Info.get_instance().danger_zone_component_distribution = DZL.get_distribution()

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
    # Info.get_instance().bpdg_neighbors_distribution = BPD.get_neighbors_distribution()
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

    pl = Pipeline()
    pl.files = FILES
    pl.topology = TOPOLOGY
    pl.r = R
    pl.dzl = DZL
    pl.cl = CL
    pl.bpd = BPD
    pl.lb_model = None

    if full:
        solvers = [S.Solver(S.LP_FULL, pl)]
    else:
        solvers = []

    solvers.extend([
        # S.Solver(S.LP_ITERATIVE, pl),
        S.Solver(S.LP_TOP_LEVEL, pl),
        S.Solver(S.H_NEIGH_FIRST, pl),
        S.Solver(S.H_COST_FIRST, pl),
        S.Solver(S.H_AVG_COST_FIRST, pl)
    ])

    Info.get_instance().results = []

    for s in solvers:
        try:
            s.solve()
            e = s.solution()
            s.check_edges()
            s.compare_to_bound()
            l_out.write_paths(f'{FILES["g_r_path_data"]}/{s.method}_edges.txt', e)
        except Exception as e:
            logging.critical(e)
            logging.critical("Something went terribly wrong, im sorry.")
    if full:
        try:
            pl.lb_model.write(f'{FILES["g_r_path_data"]}/lp_full_model.lp')
        except:
            logging.warning("LB model cound not be written to file")

    # plot(FILES)

    if not Info.get_instance().results:
        Info.get_instance().__delattr__('results')
    else:
        Info.get_instance().success = True

    Info.write_run_info(FILES)
    Info.reset()

