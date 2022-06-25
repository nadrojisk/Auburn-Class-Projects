""" Module that allows a quick benchmark of all the problems listed in the
problem directory. Currently only runs random search algorithm
"""

#!/usr/bin/env python3

import os
import solver
import glob
import time

start = time.time()
configs = os.listdir('./config')
for file in sorted(os.listdir('./problems')):
    problem = file.split('.')[0]

    configs = glob.glob(f'./config/{problem}*')
    for config in configs:
        print(f"Running {config} with ./problems/{file}")
        solver.Solver(config, verbose=True).run(f'./problems/{file}')

print(f"Runtime: {time.time() - start}")
