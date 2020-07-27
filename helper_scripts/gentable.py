import xml.etree.ElementTree as ET

def cut(num):
    data = num.split(".")
    if len(data) == 2:
        return data[0] + "." + data[1][:2]
    return num


def fit(tag, attr):
    try:
        return cut(tag.find(attr).text)
    except Exception as e:
        return "-"


filename = "0721"
infile = f'../xml_process/{filename}.xml'

with open(infile) as file:
    data = file.read()
    root = ET.fromstring(data, parser=ET.XMLParser(encoding='utf-8'))

TABLE = [['name',
         'V',
         'E',
         'edge total len',
         's lp cost',
         's lp runtime',
         's h cost',
         's h runtime',
         'm lp cost',
         'm lp runtime',
         'm h cost',
         'm h runtime']]

for topology in root:
    # graph
    graph = topology[0]
    xd = graph.find('name').text
    xd = xd.replace('_', '-')
    hehe = float(graph.find('total_edge_length').text) / float(graph.find('scale_factor').text)
    RECORD = [xd,
              graph.find('num_vertices').text,
              graph.find('num_edges').text,
              cut(str(hehe))]

    # runs
    small_found = False
    med_found = False
    for run in topology[1]:
        if fit(run, 'r_info') == 'rw_10':
            small_found = True
            lpf_found = False
            hcf_found = False
            for result in run:
                if fit(result, 'algorithm') == 'lp_full':
                    lpf_found = True
                    RECORD.append(fit(result, 'new_edges_in_km'))
                    RECORD.append(fit(result, 'runtime'))
                if fit(result, 'algorithm') == 'h_cost_first':
                    hcf_found = True
                    RECORD.append(fit(result, 'new_edges_in_km'))
                    RECORD.append(fit(result, 'runtime'))
            if not lpf_found:
                RECORD.extend(['NA'] * 2)
            if not hcf_found:
                RECORD.extend(['NA'] * 2)
        if fit(run, 'r_info') == 'rw_80':
            med_found = True
            lpf_found = False
            hcf_found = False
            for result in run:
                if fit(result, 'algorithm') == 'lp_full':
                    lpf_found = True
                    RECORD.append(fit(result, 'new_edges_in_km'))
                    RECORD.append(fit(result, 'runtime'))
                if fit(result, 'algorithm') == 'h_cost_first':
                    hcf_found = True
                    RECORD.append(fit(result, 'new_edges_in_km'))
                    RECORD.append(fit(result, 'runtime'))
            if not lpf_found:
                RECORD.extend(['NA'] * 2)
            if not hcf_found:
                RECORD.extend(['NA'] * 2)
        continue

    if not small_found:
        RECORD.extend(['NA']*4)
    if not med_found:
        RECORD.extend(['NA']*4)

    TABLE.append(RECORD)


def sep(record):
    ret = ""

    for d in record:
        ret += d + " & "
    ret = ret.rstrip('& ')
    ret += ' \\\\\n'
    return ret


with open(f'../xml_process/{filename}.tex', 'w') as f:
    f.write('\\begin{center}\n')
    f.write('\\begin{adjustbox}{max width=\\textwidth}\n')
    f.write("""""")
    f.write('\\begin{tabular}{c | c c c || c c | c c || c c | c c}\n')
    for r in TABLE:
        f.write(sep(r))
        f.write('\\hline\n')
    f.write('\\hline\n')
    f.write('\\end{tabular}\n')
    f.write('\\end{adjustbox}\n')
    f.write('\\end{center}\n')
