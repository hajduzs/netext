import os
import xml.etree.ElementTree as ET
import re


def get_element_from_file(xml_file):
    with open(xml_file) as file:
        data = file.read()
        # for older results
        data = re.sub(r'<([0-9]*)>([0-9]*)</[0-9]*>',
                      r'<dist_data>'
                      r'<value>\1</value>'
                      r'<count>\2</count>'
                      r'</dist_data>',
                      data)
        data = re.sub(r'<r>(.*)</r>',
                      r'<radius>\1</radius>',
                      data)
        data = re.sub(r'<graph name="(.*)">',
                      r'<graph><name>\1</name>',
                      data)

        return ET.fromstring(data, parser=ET.XMLParser(encoding='utf-8'))


o_dir = "/home/zsombor/Desktop/output"
o_dir = "/home/zsombor/work/netext/output"

# get graph names
graphs = []
for (dp, dn, fns) in os.walk(o_dir):
    graphs = dn
    break

root = ET.Element('root')

# walk every graph directory
for x in graphs:
    # get the topology infos
    g_tag = ET.SubElement(root, 'topology')
    t_info = f'{o_dir}/{x}/topology_info.xml'
    topology_tag = get_element_from_file(t_info)
    g_tag.append(topology_tag)
    runs = ET.SubElement(g_tag, 'runs')
    # get every of the r_ subdirectories
    subdirs = next(os.walk(f'{o_dir}/{x}'))[1]
    for subdir in subdirs:
        r_info = f'{o_dir}/{x}/{subdir}/run_info.xml'
        if not os.path.exists(r_info):
            continue
        run_tag = get_element_from_file(r_info)
        if run_tag.find("success") is None:
            continue

        # change <lp_ and <heur_ result tags to
        # <result> <algorithm> lp/heur structure
        # and make sure they are at the end of it
        if run_tag.find("success").text == "True":

            lpr = ET.Element('result')
            lp_results = run_tag.find('lp_results')
            if lp_results is not None:
                l_alg = ET.SubElement(lpr, 'algorithm')
                l_alg.text = 'lp'
                for c in lp_results:
                    lpr.append(c)
                run_tag.append(lpr)
                run_tag.remove(lp_results)

            ler = ET.Element('result')
            lp_e_results = run_tag.find('lp_eased_results')
            if lp_e_results is not None:
                lpe_alg = ET.SubElement(ler, 'algorithm')
                lpe_alg.text = 'lp_eased'
                for c in lp_e_results:
                    ler.append(c)
                run_tag.append(ler)
                run_tag.remove(lp_e_results)

            hr = ET.Element('result')
            heur_results = run_tag.find('heur_results')
            if heur_results is not None:
                h_alg = ET.SubElement(hr, 'algorithm')
                h_alg.text = 'heur'
                for c in heur_results:
                    hr.append(c)
                run_tag.remove(heur_results)
                run_tag.append(hr)

        runs.append(run_tag)

with open("measurement_merged.xml", 'w') as f:
    md = ET.tostring(root)
    f.write(md.decode('utf-8'))
