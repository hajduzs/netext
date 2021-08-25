# Geometric Network Augmentation solver

Welcome! This is our repository containing our implementation of the GNA problem 
in python.

### Paper:

["On Network Topology Augmentation for Global Connectivity under Regional Failures"](https://ieeexplore.ieee.org/document/9488879).

### Authors: 

_János Tapolcai, Zsombor László Hajdú and Alija Pašić (Budapest University of Technology and Economics, Hungary); 
Pin-Han Ho (University of Waterloo, Canada); 
Lajos Rónyai (Budapest University of Technology and Economics (BME), Hungary)_

## Repository structure 

IMPORTANT note by Zsobmor: This repo is "under construction" Right now. The original code had really bad quality and inconsistencies, so I've decided to refactor the whole thing. Until I'm done cleaning the mess I've made, a simpler and dumber version is published in place of the original. While at the moment it lacks the proper logging and measurement tools, it should stil be enough for some simpler demonstrations.

The main components and the structure of the repo are listed here: 

`/src`         -- Most of the implementation (python), excluding path planning and partitioning, see "Other packages and tools" section

`/data`       -- Input graphs.

`/res`      -- Simulation results in raw format

## How to use

- In order to run the scripts, install the required python packages with 
`pip install -r requirements.txt`
  
- Add graphs to the `/data` folder. Supported formats: `.gml`, `.lgf` or `.graphml`

- run `python3`, then `from src.run import run` and call the `run` function with the input graph, disaster radius and desired methods (dor the metohds, see `src.solver.methods`) Example: `run('data/test.lgf', 50, ['lp_full', 'h_cost_first'])` 

NOTE: If the library or the executable is not working, compile the c++ components locally as well. (See intructions in the respective repos listed in the "Other packages and tools" section).


## Other packages and tools

The code uses two submodules written in c++ for performance reasons. You can find them here: 

- The partitioning submodule can be found at [hajduzs/simplepartitions](https://github.com/hajduzs/simplepartitions)

- The route-finding submodule can be found at [hajduzs/offroute](https://github.com/hajduzs/offroute)