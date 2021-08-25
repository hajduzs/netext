"""In this module, we gather possible solver methods."""

import src.netext.solver.algs as alg

# Define constants for algorithm assigment
LP_FULL = 'lp_full'
LP_TOP_LEVEL = 'lp_top_level'
LP_ORIGINAL = 'lp_orig'
LP_ITERATIVE = 'lp_iterative'
H_COST_FIRST = 'h_cost_first'
H_NEIGH_FIRST = 'h_neigh_first'
H_AVG_COST_FIRST = 'h_avg_cost_first'


# Put them into a dict for easier use
METHODS = {
    LP_FULL: alg.lp_full,
    LP_ORIGINAL: alg.lp_first,
    H_COST_FIRST: alg.h_cost,
    H_NEIGH_FIRST: alg.h_neigh,
    H_AVG_COST_FIRST: alg.h_avg_cost
}
