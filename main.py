from datetime import datetime

import my_functions as func
from Utilities.Logging import log, set_out
from NetworkModels.DangerZones import DangerZoneList, DangerZone, reset_counter
from Utilities.HitDetection import is_face_valid_dangerzone, hit_graph_with_disaster
from NetworkModels.BipartiteGraph import BipartiteDisasterGraph
from Wrappers.PathPlanner import PathPlanner
from Utilities.Plotting2 import plot_graph_all_2, plot_graph_with_node_labels

import Utilities.Geometry2D as CustomGeom
from Wrappers.PlanarDivider import get_division_from_json

import json
import os
import shapely.geometry as geom
import networkx as nx
import mip
import itertools

# GLOBAL VARIABLES

GAMMA = 1.07

# paths

graphlist = []

for (dp, dn, filenames) in os.walk("graphs/"):
    graphlist.extend(filenames)
    break

if not os.path.exists("output"):
    os.mkdir("output")

now = datetime.now().strftime('%Y%m%d-%H%M%S')
os.mkdir("output/{}".format(now))

for g in graphlist:

    # MAKE OUTPUT FOLDER

    gpath = "output/{}/{}".format(now, g.split('.')[0])
    os.mkdir(gpath)      # We don't need to check if it already exists, because filenames are unique.

    # GENERATE JSON FROM LGF

    js = func.generate_json_from_lgf("graphs/"+g)
    jsname = gpath + "/" + g.split(".")[0] + ".json"
    with open(jsname, "w") as f:
        f.write(js)

    # LOAD TOPOLOGY AND APPEND IT WITH DATA

    TOPOLOGY = func.load_graph_form_json(jsname)
    bb = func.calculateBoundingBox(TOPOLOGY)

    func.append_data_with_edge_chains(TOPOLOGY)
    plot_graph_with_node_labels(gpath + "/labels.jpg", TOPOLOGY)

    # CALCULATE FEASIBLE R VALUES

    small_side = min(bb["x_max"] - bb["x_min"], bb["y_max"] - bb["y_min"])

    R_values = [small_side * scale / 100 for scale in range(5, 16)]

    for R in R_values[3:4]:
        g_r_path = gpath + "/r{}".format(R)
        os.mkdir(g_r_path)
        set_out(g_r_path + "/log.txt")

        # GENERATE DANGER ZONES

        DZL = DangerZoneList()

        for face in get_division_from_json(R, jsname, "{}/faces.txt".format(g_r_path)):
            #try:
            poly = geom.Polygon(func.destringify_points(face))

            if not poly.is_valid:
                poly = poly.buffer(0)

            p = poly.representative_point()

            G = hit_graph_with_disaster(TOPOLOGY, R, (p.x, p.y))

            if is_face_valid_dangerzone(GAMMA, poly, R, G):
                dz = DangerZone(G, poly, face)
                DZL.add_danger_zone(dz)

            #except Exception as e:
                #log("### EXCEPTION ####\n", "DZ_CONSTRUCTION")
                #log(repr(e), "DZ_CONSTRUCTION")
                #log("\nface:\n{}\n".format(face), "DZ_CONSTRUCTION")

        log(DZL, "DZ_CONSTRUCTION")

        # GENERATE CUTS FROM DANGER ZONES

        CL = DZL.generate_disaster_cuts()
        log(CL, "CUT_CONSTRUCTION")

        # CONSTRUCT THE BIPARTITE DISASTER GRAPH

        BPD = BipartiteDisasterGraph(CL)
        log(BPD, "BIPARTITE_CONSTRUCTION")

        # SET UP PATH PLANNER

        PP = PathPlanner()
        PP.setR(R)

        # load danger zones into the path planner
        for dz in DZL:
            PP.addDangerZone(dz.string_poly)

        # TODO:
        # LP problem

        # Model 1 with every constraint

        MODEL = mip.Model()
        X = [MODEL.add_var(var_type=mip.CONTINUOUS) for i in range(0, len(DZL))]

        # constraintek feltöltése

        for n, d in BPD.graph.nodes(data=True):
            if d["bipartite"] == 1: continue

            # get ccordinates
            pnodes = d["vrtx"].edge
            pi = func.get_coords_for_node(pnodes[0], TOPOLOGY)
            pg = func.get_coords_for_node(pnodes[1], TOPOLOGY)

            # get adjacent danger zones
            neigh_cuts = [v for v in BPD.graph.nodes if BPD.graph.has_edge(n, v)]
            d["neigh"] = len(neigh_cuts)
            ids = set()
            for c in neigh_cuts:
                ids.update(BPD.return_ids_for_cut(c))
            ids = list(ids)

            for i in range(1, len(ids)):
                i_subsets = itertools.combinations(ids, i)
                for subs in i_subsets:
                    PP.calculate_r_detour(pi, pg, ids)
                    MODEL += mip.xsum([ X[k] for k in ids ]) <= PP.getCost()

        for i in range(0, len(DZL)):
            MODEL += X[i] != 0

        MODEL.objective = mip.maximize(mip.xsum(X))

        #max egy percig fusson
        status = MODEL.optimize(max_seconds=60)

        print('solution:')
        for v in MODEL.vars:
            print('{} : {}'.format(v.name, v.x))

        # HEUR STEP 1: CALCULATE DETOUR COST FOR EVERY EDGE VERTEX SO
        # EVERY DANGER ZONE ADJACENT IS AVOIDED.

        for n, d in BPD.graph.nodes(data=True):
            if d["bipartite"] == 1:
                continue

            # get ccordinates
            pnodes = d["vrtx"].edge
            pi = func.get_coords_for_node(pnodes[0], TOPOLOGY)
            pg = func.get_coords_for_node(pnodes[1], TOPOLOGY)

            # get adjacent danger zones
            neigh_cuts = [v for v in BPD.graph.nodes if BPD.graph.has_edge(n, v)]
            d["neigh"] = len(neigh_cuts)
            ids = set()
            for c in neigh_cuts:
                ids.update(BPD.return_ids_for_cut(c))
            ids = list(ids)

            # calculate cost
            PP.calculate_r_detour(pi, pg, ids)
            cost = PP.getCost()
            path = PP.getPath()

            # update node
            d["path"] = path
            d["cost"] = cost
            d["ids"] = set(ids)

        # HEUR STEP 2: get minimum edge cover

        H = BPD.graph.copy()

        nodes = []
        while True:
            if len(dict(H.nodes).items()) == 0:
                break
            maxn = max(dict(H.nodes).items(), key=lambda x: (x[1]["neigh"], -x[1]["cost"]))  # max neigh, then cost
            if maxn[1]["neigh"] == 0:
                break
            nodes.append(maxn)

            # delete cuts protected and node selected

            H.remove_nodes_from([v for v in H.nodes if H.has_edge(maxn[0], v)])
            H.remove_node(maxn[0])

            for n, d in H.nodes(data=True):
                if d['bipartite'] is 0:
                    neigh_cuts = [v for v in H.nodes if H.has_edge(n, v)]
                    d["neigh"] = len(neigh_cuts)

        # HEUR STEP 3: OPTIMIZING ON THESE NEW EDGES

        # get every danger zone that is avoided by two or more edges

        multiples = set()
        for i in range(0, len(nodes)):
            for j in range(i + 1, len(nodes)):
                multiples.update(nodes[i][1]["ids"].intersection(nodes[j][1]["ids"]))

        for Z in multiples:
            # get corresponding edges
            corr = [n for n in nodes if Z in n[1]["ids"]]
            # set theoretical new edge cost and path for all (not containing Z)
            for n, d in corr:
                # get coordinates
                pnodes = d["vrtx"].edge
                pi = func.get_coords_for_node(pnodes[0], TOPOLOGY)
                pg = func.get_coords_for_node(pnodes[1], TOPOLOGY)

                # get adjacent danger zones
                neigh_cuts = [v for v in BPD.graph.nodes if BPD.graph.has_edge(n, v)]
                ids = set()
                no_removal = True
                for c in neigh_cuts:
                    ids.update(BPD.return_ids_for_cut(c))
                    if Z in ids:
                        ids.remove(Z)
                        no_removal = False
                if no_removal:
                    break
                ids = list(ids)

                # calculate cost
                PP.calculate_r_detour(pi, pg, ids)
                cost = PP.getCost()
                path = PP.getPath()

                # update node
                d["t_path"] = path
                d["t_cost"] = cost
                d["t_ids"] = set(ids)

                '''
                print("{} {}".format(n, (d["cost"], d["ids"])))
                print("{} {}".format(n,(d["t_cost"], d["t_ids"])))
                print("diff: {}".format(d["cost"] - d["t_cost"]))
                '''

            min_n = 0
            min_d = 0
            # select minimal cost edge
            mincost = float("inf")
            for n, d in corr:
                if mincost > d["cost"] - d["t_cost"]:
                    mincost = d["cost"] - d["t_cost"]
                    min_n = n
                    min_d = d

            # set that in the graph
            for n, d in corr:
                if n == min_n:
                    continue
                BPD.graph.nodes[n]["cost"] = d["t_cost"]
                BPD.graph.nodes[n]["path"] = d["t_path"]
                BPD.graph.nodes[n]["ids"] = d["t_ids"]

            # delete other edges
            for n, d in corr:
                if n == min_n:
                    continue
                for v in [v for v in BPD.graph.nodes if BPD.graph.has_edge(n, v) and Z in BPD.return_ids_for_cut(v)]:
                    BPD.graph.remove_edge(n, v)

        # comparing the solution with the model

        evs_to_remove = set([n for n, d in BPD.graph.nodes(data=True) if d["bipartite"] == 0]) - set([n for n, d in nodes])
        BPD.graph.remove_nodes_from(evs_to_remove)

        acsum = 0
        for n, d in BPD.graph.nodes(data=True):
            if d["bipartite"] == 1:
                continue
            acsum += d["cost"]
            cuts = [v for v in BPD.graph.nodes if BPD.graph.has_edge(n, v)]
            protected_ids = set()
            for c in cuts:
                protected_ids.update(BPD.return_ids_for_cut(c))
            lowerbound = sum([MODEL.vars[id].x for id in protected_ids])
            print("ids: {}".format(protected_ids))
            print("compare done for edge {}. LB: {} AC: {} .. diff: {} (+{}%)".format(n, lowerbound, d["cost"], d["cost"] - lowerbound, 100*(d["cost"] - lowerbound)/lowerbound))

        lbsum = sum([MODEL.vars[i].x for i in range(0, len(DZL))])
        print("In total: LB: {}, AC: {} .. diff: {} (+{}%)".format(lbsum, acsum, acsum-lbsum, 100*(acsum-lbsum)/lbsum))
        # 4. AFTERWORK: only the selected edges (nodes) need to be in the graph.

        evs_to_remove = set(BPD.graph.nodes) - set([n for n, d in nodes])
        BPD.graph.remove_nodes_from(evs_to_remove)

        # PLOTTING

        plot_graph_all_2(g_r_path, TOPOLOGY, DZL, CL, BPD, bb, R)


        ## ADDITIONAL INFORMATION

        datatdict = dict()
        leghtsum = 0
        for u, v, d in TOPOLOGY.edges(data=True):
            x = d['points'][0]
            y = d['points'][1]
            leghtsum += CustomGeom.point_to_point(x, y)

        datatdict["Total_edge_lenght"] = leghtsum

        n_edges = len(TOPOLOGY.edges)
        n_nodes = len(TOPOLOGY.nodes)
        datatdict["Number_of_edges"] = n_edges
        datatdict["Number_of_nodes"] = n_nodes

        datatdict["node_connectivity"] = nx.node_connectivity(TOPOLOGY)
        datatdict["edge_connectivity"] = nx.edge_connectivity(TOPOLOGY)

        datatdict["Avg_edge_lenght"] = leghtsum / n_edges

        new_edges = [func.destringify_points(d['path']) for n, d in BPD.graph.nodes(data=True)]
        newlengthsum = 0
        for path in new_edges:
            x = path[0]
            for j in range(1, len(path)):
                y = path[j]
                newlengthsum += CustomGeom.point_to_point(x, y)
                x = y
        n_newedges = len(new_edges)

        datatdict["Number_of_new_edges"] = n_newedges
        datatdict["Total_new_edge_lenght"] = newlengthsum
        datatdict["Avg_new_edge_lenght"] = newlengthsum / n_newedges

        datatdict["New_ratio_to_total"] = 100 * newlengthsum / leghtsum
        datatdict["New_avg_length"] = (leghtsum + newlengthsum) / (n_edges + n_newedges)

        node_degrees = TOPOLOGY.degree(TOPOLOGY.nodes)
        avg_degree = sum(d for n, d in node_degrees) / n_nodes

        datatdict["Avarage_degree"] = avg_degree
        datatdict["Disaster_R"] = R

        f = open(g_r_path + "/out.json", "w")
        f.write(json.dumps(datatdict))
        f.close()
