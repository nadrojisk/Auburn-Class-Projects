#!./env/bin/python
""" Module that is used by users to interact with the gpac framework.
Uses the argparse library to help with passing of command line arguments"""


import argparse
import game
import solver

parser = argparse.ArgumentParser(
    description='Genetic Programming Framework for Solving Pac-Man')

parser.add_argument('map', help='path to problem file')

run_group = parser.add_mutually_exclusive_group(required=True)


run_group.add_argument('-c', '--config', help='path to configuration file')
run_group.add_argument('-d', '--demo', help='demo pacman game',
                       action='store_true', default=False)

output_group = parser.add_mutually_exclusive_group()
output_group.add_argument('-p', '--progress', help='Show progress bar',
                          action='store_true', default=False)
output_group.add_argument('-b', '--board', help='Show board',
                          action='store_true', default=False)

args = parser.parse_args()

if args.demo:
    game.play(args.map)

else:
    instance = solver.Solver(args.config, show_progress_bar=args.progress, show_board=args.board)
    instance.run(args.map)
