import algorithms.graph_reading
from Utilities.Data import write_topology_info
from algorithms import helper_functions as func
from Utilities.Timeit import Timeit

from run import run
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

for g in func.load_graph_names(FILES):

    # Create overall output directory for a specific graph
    func.create_output_directory(FILES, g)

    # Generate (or read, if it already exists) JSON from input file
    Timeit.init('start')
    if func.generate_or_read_json(FILES, g) is None:
        logging.critical("Could not generate JSON")
        continue
    Timeit.time('json_generation')

    # Load topology, append it with data, create bounding box
    TOPOLOGY = algorithms.graph_reading.load_graph_form_json(FILES['js_name'])
    func.append_data_with_edge_chains(TOPOLOGY)

    # Write topology specific info to XML file
    write_topology_info(TOPOLOGY, FILES)

    # get feasible-looking values for R and run the algorithms
    rv = func.get_r_values(TOPOLOGY)[0:2]
    for R, r_comment in rv:
        run(TOPOLOGY, GAMMA, FILES.copy(), R, r_comment, g)
