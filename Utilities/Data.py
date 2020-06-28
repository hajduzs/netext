import networkx as nx
import xml.etree.ElementTree as ET

from Utilities.Geometry2D import point_to_point


class Info(object):
    glob_info = None
    original_total_edge_length = 0

    @staticmethod
    def get_instance():
        if Info.glob_info is None:
            Info.glob_info = Info()
        return Info.glob_info

    @staticmethod
    def reset():
        Info.glob_info = None

    @staticmethod
    def write_run_info(files):
        wri(files)


def wri(files):
    obj = Info.get_instance()
    with open(f'{files["g_r_path"]}/run_info.xml', 'w') as f:
        run = ET.Element('run')
        attributes = [a for a in dir(obj) if not a.startswith('__') and not callable(getattr(obj, a))]
        attributes.remove('glob_info')
        attributes.remove('original_total_edge_length')
        for attr in attributes:
            data = obj.__getattribute__(attr)
            if type(data) is list:
                se = ET.SubElement(run, attr)
                for k, v in data:
                    sse = ET.SubElement(se, 'dist_data')
                    sse_value = ET.SubElement(sse, 'value')
                    sse_value.text = str(k)
                    sse_count = ET.SubElement(sse, 'count')
                    sse_count.text = str(k)

                continue

            if type(data) is dict:
                se = ET.SubElement(run, attr)
                for k, v in data.items():
                    sse = ET.SubElement(se, str(k))
                    sse.text = str(v)
                continue

            se = ET.SubElement(run, attr)
            se.text = str(data)

        # write to file
        md = ET.tostring(run)
        f.write(md.decode('utf-8'))


def write_topology_info(topology: nx.Graph, files):
    with open(f'{files["g_path"]}/topology_info.xml', 'w') as f:
        graph = ET.Element('graph')
        graph.set('name', topology.name)

        # number of vertices
        num_vertices = ET.SubElement(graph, 'num_vertices')
        num_vertices.text = str(topology.number_of_nodes())

        # number of edges
        num_edges = ET.SubElement(graph, 'num_edges')
        num_edges.text = str(topology.number_of_edges())

        # average degree and distribution
        dist = dict()
        total_degree = 0
        for n in topology.nodes():
            d = topology.degree[n]
            total_degree += d
            if d in dist:
                dist[d] += 1
            else:
                dist[d] = 1
        dist = list(dist.items())
        dist.sort()

        degree_distribution = ET.SubElement(graph, 'degree_distribution')
        for k, v in dist:
            sse = ET.SubElement(degree_distribution, 'dist_data')
            sse_value = ET.SubElement(sse, 'value')
            sse_value.text = str(k)
            sse_count = ET.SubElement(sse, 'count')
            sse_count.text = str(k)

            continue
            degree = ET.SubElement(degree_distribution, 'value')
            degree.set('degree', str(k))
            count = ET.SubElement(degree, 'count')
            count.text = str(v)

        avg_degree = ET.SubElement(graph, 'avg_degree')
        avg_degree.text = str(total_degree / topology.number_of_nodes())

        # average and total edge length
        total_length = 0
        minl = float('inf')
        maxl = 0
        for u, v, d in topology.edges(data=True):
            l = point_to_point(*d['points'])
            if minl > l:
                minl = l
            if maxl < l:
                maxl = l
            total_length += l

        Info.original_total_edge_length = total_length
        total_edge_length = ET.SubElement(graph, 'total_edge_length')
        total_edge_length.text = str(total_length)

        max_e_l = ET.SubElement(graph, 'max_edge_length')
        max_e_l.text = str(maxl)
        min_e_l = ET.SubElement(graph, 'min_edge_length')
        min_e_l.text = str(minl)

        avg_edge_length = ET.SubElement(graph, 'avg_edge_length')
        avg_edge_length.text = str(total_length / topology.number_of_edges())

        # write to file
        md = ET.tostring(graph)
        f.write(md.decode('utf-8'))
