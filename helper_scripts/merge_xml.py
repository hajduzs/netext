import os
import xml.etree.ElementTree as ET

def get_element_from_file(xml_file):
    with open(xml_file) as file:
        data = file.read()
        return ET.fromstring(data, parser=ET.XMLParser(encoding='utf-8'))


o_dir = "/home/zsombor/Desktop/justindia/"
#o_dir = "/home/zsombor/work/netext/output"

filename = "indi"
outfile = f'../xml_process/{filename}.xml'

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
    found_s = False
    for subdir in subdirs:
        r_info = f'{o_dir}/{x}/{subdir}/run_info.xml'
        if not os.path.exists(r_info):
            continue
        run_tag = get_element_from_file(r_info)
        if run_tag.find("success") is None or run_tag.find("success").text != "True":
            continue

        found_s = True
        rkm = ET.SubElement(run_tag, 'r_in_km')
        rkm.text = run_tag.find("r_info").text.split('_')[-1]
        runs.append(run_tag)

    if not found_s:
        root.remove(g_tag)

with open(outfile, 'w') as f:
    md = ET.tostring(root)
    f.write(md.decode('utf-8'))

# for older results
'''
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
data = re.sub(r'<time>([0-9]*).([0-9]*)</time>',
              r'<runtime>\1.\2</runtime>',
              data)
'''
