import xml.etree.ElementTree as ET


def cut(num):
    data = num.split(".")
    if len(data) == 2:
        if len(data[0]) > 1:
            return data[0]
        if data[0] == data[1] == '0':
            return str(0)
        return data[0] + "." + data[1][:2]
    return num


def fit(tag, attr):
    try:
        return tag.find(attr).text
    except Exception as e:
        print(attr, tag)
        return "X"

def perc(num):
    print(num)
    return cut(str(float(num) * 100))

def getspec(RECORD, res):
    RECORD.append(perc(fit(res, 'new_edges_ratio_to_total')))
    RECORD.append(fit(res, 'new_edges_count'))
    RECORD.append(cut(fit(res, 'runtime')))


def sub(r, RECORD):
    lpf_f = False
    hcf_f = False
    lrr = []
    hrr = []
    for res in r:
        if fit(res, 'algorithm') == 'lp_full':
            lpf_f = True
            getspec(lrr, res)
        if fit(res, 'algorithm') == 'h_cost_first':
            hcf_f = True
            getspec(hrr, res)
    if not lpf_f:
        RECORD.extend(['-'] * 3)
    else:
        RECORD.extend(lrr)
    if not hcf_f:
        RECORD.extend(['-'] * 3)
    else:
        RECORD.extend(hrr)


filename = "0721"
infile = f'../xml_process/{filename}.xml'

with open(infile) as file:
    data = file.read()
    root = ET.fromstring(data, parser=ET.XMLParser(encoding='utf-8'))

TABLE = [['% HEADER']]

for topology in root:
    # graph
    graph = topology[0]
    xd = graph.find('name').text
    xd = xd.replace('_', '-')
    print(f' --- --- {xd}')
    hehe = float(graph.find('total_edge_length').text) / float(graph.find('scale_factor').text)
    RECORD = [xd,
              graph.find('num_vertices').text,
              graph.find('num_edges').text,
              cut(str(hehe))]

    # runs
    small_found = False; srr = []
    med_found = False; mrr = []
    big_found = False; brr = []
    for run in topology[1]:
        if fit(run, 'r_info') == 'rw_10':
            small_found = True
            sub(run, srr)
        if fit(run, 'r_info') == 'rw_40':
            med_found = True
            sub(run, mrr)
        if fit(run, 'r_info') == 'rw_80':
            big_found = True
            sub(run, brr)

        continue

    if not small_found:
        RECORD.extend(['--'] * 6)
    else:
        RECORD.extend(srr)

    if not med_found:
        RECORD.extend(['--'] * 6)
    else:
        RECORD.extend(mrr)

    if not big_found:
        RECORD.extend(['--'] * 6)
    else:
        RECORD.extend(brr)

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
