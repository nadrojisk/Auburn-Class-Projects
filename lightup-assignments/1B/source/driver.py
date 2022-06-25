#!/linux_apps/python-3.6.1/bin/python3
""" Module that is used by users to interact with the solver framework.
Uses the argparse library to help with passing of command line arguments"""


import argparse
import solver


parser = argparse.ArgumentParser(
    description='Evolutionary Algorithms for Solving NP-Complete Light Up Puzzle')

# run
parser.add_argument('problem', help='path to problem file')
parser.add_argument('config',  help='path to config file')
parser.add_argument('-v', '--verbose',
                    help='adds verbose output', action='store_true')

args = parser.parse_args()


solver_instace = solver.Solver(
    config_filename=args.config, verbose=args.verbose)
solver_instace.run(args.problem)
