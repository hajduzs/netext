def write_dangerzones(fp, dzl):
    with open(fp, "a+") as f:
        f.write("id;poly\n")
        for zone in dzl:
            f.write("{};{}".format(zone.id, zone.string_poly))


def write_cuts(fp, cl):
    with open(fp, "a+") as f:
        f.write("id;zones\n")
        for c in cl:
            f.write("{};{}\n".format(c.id, c.dangerZones))


def write_paths(fp, paths):
    with open(fp, "a+") as f:
        f.write("edge;path;cost;zones\n")
        for e in paths:
            f.write("{};{};{};{}\n".format(e[0], e[1], e[2], e[3]))
