import os
from algorithms.helper_functions import destringify_points


o_dir = "/home/zsombor/Desktop/netext_mindenkori/0721/output"

# get graph names
graphs = []
for (dp, dn, fns) in os.walk(o_dir):
    graphs = dn
    break

DOUBLE = []
simple = 0

for x in graphs:
    subdirs = next(os.walk(f'{o_dir}/{x}'))[1]
    for subdir in subdirs:
        edgefiles=[
        f'{o_dir}/{x}/{subdir}/data/h_cost_first_edges.txt',
        f'{o_dir}/{x}/{subdir}/data/h_avg_cost_first_edges.txt',
        f'{o_dir}/{x}/{subdir}/data/h_neigh_first_edges.txt',
        f'{o_dir}/{x}/{subdir}/data/lp_full_edges.txt',
        f'{o_dir}/{x}/{subdir}/data/lp_top_level_edges.txt'
        ]
        for ef in edgefiles:
            try:
                with open(ef) as f:
                    lines = f.readlines()
                    paths = [destringify_points(l.split(";")[1]) for l in lines[1:]]
                    for p in paths:
                        if p[0] == p[-1]:
                            DOUBLE.append(''.join(ef.split('/')[-1].split('_')[:-1]) + ' -- ' + x + " -- " + subdir)
                        else:
                            simple += 1
            except:
                pass

print(f'simple edges: {simple}')
print(f'double edges: {len(DOUBLE)}')
print('Double stats:')
for d in DOUBLE:
    print(d)