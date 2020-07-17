from algorithms.Pipeline import Pipeline
from algorithms.lb_calc import dual_lp_lb_calc
from algorithms.heuristic_calc import heuristic_calc
from NetworkModels.ConstarintGraph import ConstraintGraph
from Utilities.Timeit import Timeit


def lp_full(p: Pipeline):
    Timeit.init()
    m, cl = dual_lp_lb_calc(p, full=True, iterate=False)
    cg = ConstraintGraph(m.constrs)
    edges = cg.optimize(cl)
    t = Timeit.time('lp_full')
    p.lb_model = m
    return edges, t, len(m.constrs)


def lp_top_lvl(p: Pipeline):
    Timeit.init()
    m, cl = dual_lp_lb_calc(p, full=False, iterate=False)
    cg = ConstraintGraph(m.constrs)
    edges = cg.optimize(cl)
    t = Timeit.time('lp_top_lvl')
    return edges, t, len(m.constrs)


def lp_iter(p: Pipeline):
    Timeit.init()
    m, cl = dual_lp_lb_calc(p, full=False, iterate=True)
    cg = ConstraintGraph(m.constrs)
    edges = cg.optimize(cl)
    t = Timeit.time('lp_top_lvl')
    return edges, t, len(m.constrs)


def h_cost(p: Pipeline):
    Timeit.init()
    edges = heuristic_calc(p, 'C')
    t = Timeit.time('h_cost')
    return edges, t, None


def h_neigh(p: Pipeline):
    Timeit.init()
    edges = heuristic_calc(p, 'N')
    t = Timeit.time('h_cost')
    return edges, t, None


def h_avg_cost(p: Pipeline):
    Timeit.init()
    edges = heuristic_calc(p, 'A')
    t = Timeit.time('h_cost')
    return edges, t, None
