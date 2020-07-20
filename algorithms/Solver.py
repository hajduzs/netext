import algorithms.algs as alg
from algorithms.Pipeline import Pipeline
from algorithms.algoritmhs_helper_functions import check_new_edges_bounds, compare_and_log_info
import logging

# Define constants for algorithm assigment
LP_FULL = 'lp_full'
LP_TOP_LEVEL = 'lp_top_level'
LP_ITERATIVE = 'lp_iterative'
H_COST_FIRST = 'h_cost_first'
H_NEIGH_FIRST = 'h_neigh_first'
H_AVG_COST_FIRST = 'h_avg_cost_first'

# Put them into a dict for easier use
_METHODS = {
    LP_FULL: alg.lp_full,
    LP_TOP_LEVEL: alg.lp_top_lvl,
    LP_ITERATIVE: alg.lp_iter,
    H_COST_FIRST: alg.h_cost,
    H_NEIGH_FIRST: alg.h_neigh,
    H_AVG_COST_FIRST: alg.h_avg_cost
}


class Solver:
    """Solver class for the NetExt problem."""

    def __init__(self, method, pipeline: Pipeline):
        if method in _METHODS:
            self.method = method
            self._alg = _METHODS[method]
        else:
            raise Exception('Target method not implemented')
        self._pipe: Pipeline = pipeline
        # define run-specific attributes
        self._solution = None
        self._time: float = None
        self._total_constr: int = None

    def solve(self):
        edges, t, c = self._alg(self._pipe)
        self._solution = edges
        self._time = t
        if c is not None:
            self._total_constr = c

    def solution(self):
        if self._solution is None:
            raise Exception("Solution not calculated! Call .solve() first.")
        return self._solution

    def time(self):
        if self._time is None:
            raise Exception("Solution not calculated! Call .solve() first.")
        return self._time

    def check_edges(self):
        if self._solution is None:
            raise Exception("Solution not calculated! Call .solve() first.")
        logging.debug(f'Comparing edges produced by {self.method}')
        check_new_edges_bounds(self._solution, self._pipe.topology, self._pipe.r)

    def compare_to_bound(self):
        if self._solution is None:
            raise Exception("Solution not calculated! Call .solve() first.")
        compare_and_log_info(self._solution, self._pipe, self._time, self.method, self._total_constr)
