""" Module that implements a solver object for completing the lightup problem"""
from shutil import copyfile
import json
import random
import time
import collections
import lightup
import numpy as np

RunTuple = collections.namedtuple('run', 'time iterations fitness solution')


class Solver:
    """Solver object for the LightUp problem.

    config_filename -- path to the config file
    vebrose -- boolean to determine if veborse output should be printed
    """

    def __init__(self, config_filename="../config.json", verbose=False):
        with open(config_filename) as file:
            config = json.load(file)

            self.verbose = verbose
            self.algorithm = config.get('algorithm')
            self.log_file = config.get('log_file')
            self.solution_file = config.get('solution_file')
            self.max_fitness = config.get('max_fitness')
            self.num_of_runs = config.get('num_of_runs')
            self.seed = config.get('seed')
            if self.seed == 'None':
                self.seed = None
            self.evals = []
            self.shape = []
            self.ignore_black_cells = config.get('ignore_black_cells')
            if self.ignore_black_cells is None:
                self.ignore_black_cells = False

    def run(self, problem_filename):
        """Runs algorithm to attempt to solve the current problem

        problem_filename -- path to the problem file
        """
        if self.seed:
            random.seed(self.seed)
        else:
            random.seed(time.time())

        original_board = lightup.create_board(problem_filename)
        self.shape = original_board.shape
        max_fitness = 0
        best_solution = []

        if self.algorithm == "Random Search":
            if self.verbose:
                print("Running Random Search Algorithm")
            solver = self.random_solver
        with open(self.log_file, "+w") as file:
            file.write("Result Log\n\n")

        for run_count in range(self.num_of_runs):
            self.evals = []
            for _ in range(self.max_fitness):
                board = original_board.copy()
                solver(board)
            fitness, solution = self.log_run(run_count)

            if fitness > max_fitness:
                max_fitness = fitness
                best_solution = solution
        self.log_solution(max_fitness, best_solution, problem_filename)

    def random_solver(self, board):
        """Random Search solver algorithm. Randomly picks N bulbs to place
        at random open locations across the board.

        board -- RxC numpy array representing the game board, filled with bulbs,
        black cells, and light
        """

        start = time.time()

        # generate list of possible locations to place a bulb
        list_of_locations = np.where(board == lightup.NOT_LIT)
        list_of_locations = list(
            zip(list_of_locations[0], list_of_locations[1]))

        # get number of bulbs to place from [1, NUM_OF_POSSIBLE_LOCATIONS]
        num_of_bulbs_to_place = random.randint(1, len(list_of_locations))

        iterations = 0
        solution = []
        for _ in range(num_of_bulbs_to_place):
            location = random.choice(list_of_locations)
            list_of_locations.remove(location)
            board = lightup.place_bulb(board, location)
            solution.append(location)
            iterations += 1

        fitness = lightup.calculate_fitness(board, self.ignore_black_cells)
        self.evals.append(RunTuple(time.time()-start,
                                   iterations, fitness, solution))

    def log_run(self, run_count):
        """ Logs fitness for current run to file

        run_count -- current run iteration number
        """

        with open(self.log_file, "+a") as file:
            file.write(f"Run {run_count}\n")
            # starts at -1 as to log the first eval with 0 fitness
            max_fitness = -1
            solution = []
            for count, run in enumerate(self.evals):
                if run.fitness > max_fitness:
                    max_fitness = run.fitness
                    solution = run.solution
                    file.write(f"\t{count+1}\t{run.fitness}\n")
            file.write("\n")
        return max_fitness, solution

    def log_solution(self, max_fitness, best_solution, problem_filename):
        """ Log best solution out of all runs.

        max_fitness -- highest fitness achieved out of all runs
        best_solution -- best solution out of all runs
        problem_filename -- problem file that the solution matches to
        """

        # copies problem file as per specifications of the start for solution files
        copyfile(problem_filename, self.solution_file)
        if self.verbose:
            print(
                f"Logging best solution for all runs at {self.solution_file}\n")
        with open(self.solution_file, "a") as file:
            file.write(f"\n{max_fitness}\n")
            for coor in best_solution:
                # add one to offset for it starting at 1
                file.write(f"{coor[1]+1} {self.shape[0] - coor[0]}\n")
