""" Module that allows a quick benchmark of all the problems listed in the
problem directory. Currently only runs random search algorithm
"""

#!/usr/bin/env python3

import os
import solver

configs = os.listdir('./config')
for file in sorted(os.listdir('./problems')):
    problem = file.split('.')[0]
    config = f"{problem}_config.json"
    if config in configs:
        print(f"Running ./config/{config} with ./problems/{file}")
        solver.Solver(f'./config/{config}',
                      verbose=True).run(f'./problems/{file}')
