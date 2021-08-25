"""This module contains various method definitions for the solver class."""

from src.netext.Pipeline import Pipeline
from src.netext.solver.algorithms.full_lp_calc import full_lp_calc
from src.netext.solver.algorithms.greedy_heuristic import heuristic_calc
from src.netext.solver.algorithms.ilp_method import dual_lp_lb_calc
from src.netext.solver.constraintgraph import ConstraintGraph

"""Methods from here: should be straightforward"""


def lp_full(p: Pipeline):
    m, cl = dual_lp_lb_calc(p, full=True)
    cg = ConstraintGraph(m.constrs)
    edges = cg.optimize(cl)
    p.lb_model = m
    return edges, len(m.constrs)


def lp_first(p: Pipeline):
    edges = full_lp_calc(p)
    return edges, None


def h_cost(p: Pipeline):
    edges = heuristic_calc(p, 'C')
    return edges, None


def h_neigh(p: Pipeline):
    edges = heuristic_calc(p, 'N')
    return edges, None


def h_avg_cost(p: Pipeline):
    edges = heuristic_calc(p, 'A')
    return edges, None
