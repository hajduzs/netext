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
            maxn = max(dict(H.nodes).items(), key=lambda x: (x[1]["neigh"], -x[1]["cost"])) # max neigh, then cost
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
            for j in range(i+1, len(nodes)):
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

            t_sum = sum([x["t_cost"] for n, x in corr])
            min_n = 0
            min_d = 0
            # select minimal cost edge
            mincost = float("inf")
            for n, d in corr:
                if mincost > t_sum - d["t_cost"] + d["cost"]:
                    mincost = t_sum - d["t_cost"] + d["cost"]
                    min_n = n
                    min_d = d

            # set that in the graph
            BPD.graph.nodes[min_n]["cost"] = min_d["t_cost"]
            BPD.graph.nodes[min_n]["path"] = min_d["t_path"]
            BPD.graph.nodes[min_n]["ids"] = min_d["t_ids"]

        # 4. AFTERWORK: only the selected edges (nodes) need to be in the graph.

        evs_to_remove = set(BPD.graph.nodes) - set([n for n,d in nodes])
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