import os
import xml.etree.ElementTree as ET
import re


def get_element_from_file(file):
    with open(file) as f:
        # ET.parse(t_info, parser=ET.XMLParser(encoding='utf-8')).getroot()
        data = f.read()
        data = re.sub(r'<([0-9]*)>([0-9]*)</[0-9]*>',
                      r'<dist_data><value>\1</value><count>\2</count></dist_data>',
                      data)
        data = re.sub(r'<r>(.*)</r>',
                      r'<radius>\1</radius>',
                      data)
        return ET.fromstring(data, parser=ET.XMLParser(encoding='utf-8'))


root = ET.Element('root')
o_dir = "home/zsombor/Desktop/output"

graphs = []
for (dp, dn, fns) in os.walk(o_dir):
    graphs = dn
    break

for x in graphs:
    g_tag = ET.SubElement(root, x)
    t_info = f'{o_dir}/{x}/topology_info.xml'
    g_tag.append(get_element_from_file(t_info))
    runs = ET.SubElement(g_tag, 'runs')
    subdirs = next(os.walk(f'{o_dir}/{x}'))[1]
    for subdir in subdirs:
        r_info = f'{o_dir}/{x}/{subdir}/run_info.xml'
        runs.append(get_element_from_file(r_info))

with open("measurement_merged.xml", 'w') as f:
    md = ET.tostring(root)
    f.write(md.decode('utf-8'))