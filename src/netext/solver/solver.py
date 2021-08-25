import src.netext.solver.methods as meth
import logging

from src.netext.Pipeline import Pipeline
from src.measurement.timer import timer

class Solver:
    """Solver class for the NetExt problem."""

    def __init__(self, method, pipeline: Pipeline):
        if method in meth.METHODS:
            self.method = method
            self._alg = meth.METHODS[method]
        else:
            raise Exception('Target method not implemented')
        self._pipe: Pipeline = pipeline
        # define run-specific attributes
        self._solution = None
        self._total_constr: int = None

    def solve(self):
        with timer(self.method):
            edges, c = self._alg(self._pipe)
        self._solution = edges
        self._total_constr = c

    def solution(self):
        if self._solution is None:
            raise Exception("Solution not calculated! Call .solve() first.")
        return self._solution

    def check_edges(self):
        if self._solution is None:
            raise Exception("Solution not calculated! Call .solve() first.")
        logging.debug(f'Comparing edges produced by {self.method}')
        print("TODO")  # TODO
        # check_new_edges_bounds(self._solution, self._pipe.topology, self._pipe.r)

    def compare_to_bound(self):
        if self._solution is None:
            raise Exception("Solution not calculated! Call .solve() first.")
        print("TODO")  # TODO
        # compare_and_log_info(self._solution, self._pipe, self._time, self.method, self._total_constr)
