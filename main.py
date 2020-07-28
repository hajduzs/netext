import algorithms.graph_reading
from Utilities.Data import write_topology_info
from algorithms import helper_functions as func
from Utilities.Timeit import Timeit

from run import run
import os
import shutil
import logging
import argparse

# GLOBAL VARIABLES
GAMMA = 1.1    # anything wider than 120° will be ignored TODO: function to convert degrees to gamma
FILES = {}


# arguments
def dir_path(path):
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")


parser = argparse.ArgumentParser(description='NetExt main entry point')
parser.add_argument('dir', metavar='D', type=dir_path, nargs=1,
                    help='One directory where input files can be found')
parser.add_argument('-rc', metavar='R', type=str, choices=['few', '5km' 'medium', 'many'],
                    help='how many different radii to test the graphs. ')
parser.add_argument('-d', action='store_true', help='Debug mode.')
args = parser.parse_args()

graph_names = []

FILES = {'input_dir': args.dir[0]+'/'}
graph_names.extend(func.load_graph_names(FILES))

r_config = args.rc
if args.d:
    ans = input("This will delete the output directory if it exists. Continue? type 'yes'")
    if ans == "yes":
        if os.path.exists("output"):
            shutil.rmtree("output")
    else:
        print("Ok, exiting instead.")
        exit(0)
print(args.rc)
if not os.path.exists("output"):
    os.mkdir("output")

for g in graph_names:

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
    rv = func.get_r_values(TOPOLOGY, r_config)
    for R, r_comment in rv:
        run(TOPOLOGY, GAMMA, FILES.copy(), R, r_comment, g)
