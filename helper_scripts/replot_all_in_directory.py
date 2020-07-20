import os
import algorithms.Solver as S
from Utilities.Plotting import replot

o_dir = "/home/zsombor/Desktop/latest_0620_test/output"

graphs = []
for (dp, dn, fns) in os.walk(o_dir):
    graphs = dn
    break

for x in graphs:
    subdirs = next(os.walk(f'{o_dir}/{x}'))[1]
    for subdir in subdirs:
        gr = f'{o_dir}/{x}/{subdir}'
        for method in S._METHODS:
            try:
                replot(
                    x,
                    gr,
                    f'{o_dir}/{x}/{x}.json',
                    f'{gr}/data/zones.txt',
                    f'{gr}/data/cuts.txt',
                    f'{gr}/data/{method}_edges.txt',
                    float(subdir.split('_')[-1]),
                    f'_{method}'
                )
            except Exception as e:
                print(f'Plotting {method} edges for {gr} failed. Cause: {e}')