outfile = None
environment = None


def set_out(filename):
    global outfile
    outfile = open(filename, "a+")


def set_env(env):
    global environment
    environment = env


def log(message, env=environment, lvl=0):
    global environment
    if environment != "PATH_PLANNER":
        outfile.write(str(message))


# Environments so I don't forget:
'''
PLANAR_DIV                  ::      The face generating wrapper
PATH_PLANNER                ::      SIG shortest detour lib calls 
DZ_CONSTRUCTION             ::      DangerZone construction
CUT_CONSTRUCTION            ::      Cut Construction
BIPARTITE_CONSTRUCTION      ::      bpd construction
OPT                         ::      Optimizing heuristic
'''


def write_dangerzones(fp, dzl):
    with open(fp, "a+") as f:
        f.write("id;poly\n")
        for zone in dzl:
            f.write("{};{}".format(zone.id, zone.string_poly))


def write_paths(fp, paths):
    with open(fp, "a+") as f:
        f.write("edge;path;cost;zones\n")
        for e in paths:
            f.write("{};{};{};{}\n".format(e[0], e[1], e[2], e[3]))