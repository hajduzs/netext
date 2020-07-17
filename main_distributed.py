import argparse
import os

from algorithms import helper_functions as func


def dir_path(path):
    if os.path.isdir(path):
        return path
    else:
        raise argparse.ArgumentTypeError(f"readable_dir:{path} is not a valid path")


parser = argparse.ArgumentParser(description='Distributed run script for the netext '
                                             'simulations')
parser.add_argument('dirs', metavar='D', type=dir_path, nargs='+',
                    help='One or more directories where input files can be found')
parser.add_argument('-threads', metavar='T', type=int, nargs=1,
                    default=1,
                    help='Number of separate threads to start the work on.')
args = parser.parse_args()

graph_names = []
for d in args.dirs:
    graph_names.extend(func.load_graph_names({'input_dir':d+'/'}))
graph_names.sort()

print(graph_names)

num_threads = args.threads
print(num_threads)