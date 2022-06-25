""" Module that implements a solver object for completing the lightup problem. """
import itertools
from shutil import copyfile
import json
import random
import time
import logging
import lightup
import numpy as np
from individual import Individual
import tqdm


class MyException(Exception):
    pass


# Initialization Algorithms
INIT_VALID = ['validity forced']
INIT_VANILLA = ['vanilla']
INIT_ALGS = INIT_VALID + INIT_VANILLA

# Parent Selection Algorithms

PARENT_FPS = ['fitness proportional selection', 'fps']
PARENT_TOURN = ['k-tournament selection with replacement', 'tournament']
PARENT_SUS = ['sus']
PARENT_UNIFORM = ['uniform']
PARENT_ALGS = PARENT_FPS + PARENT_TOURN + PARENT_SUS + PARENT_UNIFORM

# Termination Algorithms
TERM_TOTAL_EVAL_ALG = ['number of evals till termination', 'num of evals']
TERM_NO_CHANGE_ALG = ['no change in fitness for n evals', 'n evals']
TERM_ALGS = TERM_TOTAL_EVAL_ALG + TERM_NO_CHANGE_ALG

# Recombination Algorithms
ONE_POINT = ['one point crossover']
UNIFORM = ['uniform']
RECOMB_ALGS = ONE_POINT + UNIFORM

# Survival Strategy Algorithms
PLUS = ['plus']
COMMA = ['comma', 'generation']
SURV_STRAT_ALGS = PLUS + COMMA

# Survival Selection Algorithms
SURV_TRUNC = ['truncation']
SURV_TOURN_ALGS = ['k-tournament selection without replacement', 'tournament']
SURV_UNIFORM = ['uniform']
SURV_FPS = ['fps']
SURV_ALGS = SURV_TRUNC + SURV_TOURN_ALGS + SURV_UNIFORM + SURV_FPS

# Constraint Algorithms
CON_PENALTY = ['penalty']
CON_ALGS = CON_PENALTY


class Solver:
    """Solver object for the LightUp problem.

    config_filename - path to the config file
    verbose - boolean to determine if verbose output should be printed
    """

    def __init__(self, config_filename="../config.json", verbose=False):
        self.config = config_filename
        with open(config_filename) as file:
            config = json.load(file)

            self.algorithm = config.get('algorithm')
            self.log_file = config.get('log_file')
            self.solution_file = config.get('solution_file')

            self.fitness_evals = config.get('fitness_evals')
            self.num_of_runs = config.get('num_of_runs')
            self.seed = config.get('seed')

            self.ignore_black_cells = config.get('ignore_black_cells')
            if self.ignore_black_cells is None:
                self.ignore_black_cells = False

            self.force_validity = config.get('force_validity')
            if self.force_validity is None:
                self.force_validity = False

            self.children = config.get('children')  # λ
            self.parents = config.get('parents')    # μ

            self.log_1b = config.get('log_1b')

            try:
                self.parent_algorithm = config.get('parent_alg').lower()
                self.survival_algorithm = config.get('survival_alg').lower()
                self.termination_algorithm = config.get(
                    'termination_alg').lower()
                self.initialization_algorithm = config.get(
                    'initialization_alg').lower()
                self.child_algorithm = config.get('child_alg').lower()
                self.survival_strategy_algorithm = config.get(
                    'survival_strategy_alg').lower()
                self.constraint_algorithm = config.get(
                    'constraint').lower()

            except AttributeError as error:
                print("Error: Did not provide algorithm")
                raise AttributeError from error

            self.penalty_coefficient = config.get('penalty_coefficient')
            self.mutation_rate = config.get('mutation_rate')
            self.self_adaptive_mutation = config.get('self_adaptive_mutation')
            self.self_adaptive_penalty = config.get('self_adaptive_penalty')
            # setting K for tournament
            self.tournament_parent = config.get('t_parent')
            self.tournament_survival = config.get('t_survival')

            # n runs with no change until termination
            self.n_termination = config.get('n')

            self.shape = []
            self.verbose = verbose

            if self.verbose:
                logging.basicConfig(level=logging.DEBUG, format='%(message)s')

            # ensure all passed params are valid and legal otherwise quit
            self.error_checking()

    def error_checking(self):
        """ Ensures all variables saved in object are legal."""
        # Ensure no logical errors in params

        if not isinstance(self.ignore_black_cells, bool):
            raise MyException(
                "Error: ignore_black_cells must be a boolean in config file")
        if not isinstance(self.force_validity, bool):
            raise MyException(
                "Error: force_validity must be a boolean in config file")
        if not isinstance(self.num_of_runs, int):
            raise MyException(
                "Error: num_of_runs must be an integer in config file")
        if not isinstance(self.children, int):
            raise MyException(
                "Error: children must be an integer in config file")
        if not isinstance(self.parents, int):
            raise MyException(
                "Error: parents must be an integer in config file")
        if not isinstance(self.fitness_evals, int):
            raise MyException(
                "Error: fitness_evals must be an integer in config file")
        if self.self_adaptive_mutation and self.mutation_rate:
            raise MyException(
                "Error: Cannot have self adapative mutation and provide a mutation rate")
        if self.self_adaptive_penalty and self.penalty_coefficient:
            raise MyException(
                "Error: Cannot have self adaptive penalty and provide a penalty coefficient")
        if self.survival_strategy_algorithm in ['comma', 'generation']:
            if self.children < self.parents:
                raise MyException(
                    "Error: λ should be greater than or equal to μ for comma survival strategy runs")
        if self.log_file == self.solution_file:
            raise MyException(
                "Error: Solution file and log file should have different paths")

        # Ensure passed algorithms are supported

        if self.initialization_algorithm not in INIT_ALGS:
            raise MyException(
                "Error: Provided initialization algorithm not supported")
        if self.parent_algorithm not in PARENT_ALGS:
            raise MyException(
                "Error: Provided parent selection algorithm not supported")
        if self.survival_strategy_algorithm not in SURV_STRAT_ALGS:
            raise MyException(
                "Error: Provided survival strategy algorithm not supported")
        if self.survival_algorithm not in SURV_ALGS:
            raise MyException(
                "Error: Provided survival algorithm not supported")
        if self.termination_algorithm not in TERM_ALGS:
            raise MyException(
                "Error: Provided termination algorithm not supported")
        if self.constraint_algorithm not in CON_ALGS:
            raise MyException(
                "Error: Provided constraint algorithm not supported")
        if self.child_algorithm not in RECOMB_ALGS:
            raise MyException(
                "Error: Provided recombination algorithm not supported")

    def set_seed(self):
        """Sets random seed value based on object seed variable."""

        if self.seed is None:
            self.seed = int(time.time())
        random.seed(self.seed)
        np.random.seed(self.seed)

    def run(self, problem_filename):
        """Runs algorithm to attempt to solve the current problem

        problem_filename - path to the problem file
        """
        with open(self.log_file, "+w") as file:
            file.write("Result Log\n\n")

        self.set_seed()
        original_board = lightup.create_board(problem_filename)
        self.shape = original_board.shape

        if self.algorithm == "Random Search":
            self.random_search(original_board, problem_filename)
        else:
            self.evolutionary_algorithm(original_board, problem_filename)

    ###########################################################################
    ############################# Solver ######################################
    ###########################################################################

    def random_search(self, original_board, problem_filename):
        """ Runs Random Search algorithm against provided problem file.

        original_board - RxC numpy array representing the game board,
        filled with bulbs, black cells, and light

        problem_filename - file that contains the problem to run the EA against
        """

        logging.debug("Running Random Search Algorithm")
        num_of_runs = range(self.num_of_runs)

        # self.log_experiment_config(problem_filename)

        max_ind_of_experiment = None
        best_runs = []
        for _ in num_of_runs:

            max_ind_of_run = None
            population = []
            for _ in range(self.fitness_evals):

                board = original_board.copy()
                fitness, solution, *_ = self.uniform_random(
                    board)
                population.append(Individual(
                    fitness, solution=solution))

                max_ind_of_generation = max(population)

                if max_ind_of_experiment is None or max_ind_of_experiment < max_ind_of_generation:
                    max_ind_of_experiment = max_ind_of_generation

                if max_ind_of_run is None or max_ind_of_run < max_ind_of_generation:
                    max_ind_of_run = max_ind_of_generation
            best_runs.append(max_ind_of_run)
        self.log_best_ind_per_run(best_runs)

        self.log_solution(
            max_ind_of_experiment, problem_filename)

    def evolutionary_algorithm(self, original_board, problem_filename):
        """ Runs EA with specific parameters such as parent selection, child selection,
        and termination configurable via json file.

        original_board - RxC numpy array representing the game board,
        filled with bulbs, black cells, and light

        problem_filename - file that contains the problem to run the EA against
        """

        self.log_experiment_config(problem_filename)

        logging.debug("Running EA")

        num_of_runs = range(self.num_of_runs)

        max_ind_of_experiment = None
        past_evals_with_no_change = 0
        best_runs = []
        for run in tqdm.tqdm(num_of_runs):

            self.log_run_header(run+1)

            population = self.initialize_population(original_board)
            eval_counter = len(population)

            max_ind_of_generation = max(population)
            if max_ind_of_experiment is None:
                max_ind_of_experiment = max_ind_of_generation

            max_ind_of_run = max_ind_of_generation

            self.log_generation(eval_counter, population)

            keep_going = True
            while keep_going:

                parents = self.parent_selection(population)

                children = self.child_creation(parents, original_board)
                eval_counter += len(children)

                population = self.survival_strategy_selection(
                    population, children)
                population = self.survival_selection(population)

                # log generation
                max_tmp = max(population)
                if max_ind_of_generation < max_tmp:
                    past_evals_with_no_change = 0
                    max_ind_of_generation = max_tmp
                    if max_ind_of_experiment < max_ind_of_generation:
                        max_ind_of_experiment = max_ind_of_generation
                else:
                    past_evals_with_no_change += len(children)

                if max_ind_of_run is None or max_ind_of_run < max_tmp:
                    max_ind_of_run = max_tmp

                self.log_generation(eval_counter, population)
                keep_going = self.termination_selection(
                    eval_counter, past_evals_with_no_change)
            best_runs.append(max_ind_of_run)
        self.log_best_ind_per_run(best_runs)
        self.log_solution(max_ind_of_experiment, problem_filename)

    ###########################################################################
    ###################### Algorithm Selection ################################
    ###########################################################################

    def initialization_selection(self, original_board):
        """ Generate μ-individuals for intiail generation based on chosen algorithm

        original_board - RxC numpy array representing the game board,
        filled with bulbs, black cells, and light
        """

        if self.initialization_algorithm in INIT_VALID:
            board = self.uniform_random_with_forced_validity(
                original_board)
            original_board = board

        return self.uniform_random(original_board)

    def parent_selection(self, population):
        """ Select 2λ-parents for next generation based on chosen algorithm since
        I have chosen to get with a 2->1 reproduction operator (2 parents, 1 child)

        population - list of individuals to be used to create the next generation
        """

        if self.parent_algorithm in \
                PARENT_FPS:
            population = self.fitness_proportional_selection(
                population)
        elif self.parent_algorithm in \
                PARENT_TOURN:
            population = self.tournament_selection_parent(population)
        elif self.parent_algorithm in PARENT_SUS:
            population = self.stochastic_uniform_sampling(population)
        elif self.parent_algorithm in PARENT_UNIFORM:
            population = self.uniform_random_parent(population)

        return population

    def survival_selection(self, population):
        """ Selects μ-individuals to survive into the next generation based on
        a chosen algorithm.

        population - list of old individuals from prior generation
        """

        if self.survival_algorithm in SURV_TRUNC:
            population = self.truncation(population)
        elif self.survival_algorithm in\
                SURV_TOURN_ALGS:
            population = self.tournament_selection_survival(population)
        elif self.survival_algorithm in \
                SURV_UNIFORM:
            population = self.uniform_random_survival(population)
        elif self.survival_algorithm in \
                SURV_FPS:
            population = self.fitness_proportional_selection_survival(
                population)

        return population

    def termination_selection(self, evals, past_n_evals):
        """ Determines whether to end the current run based on termination criteria.

        evals - number of current evals
        past_n_fitnesses - list of past n fitnesses
        max_ind - best individual object of current generation
        """

        if self.termination_algorithm in \
                TERM_TOTAL_EVAL_ALG:
            return self.num_of_evals(evals)
        if self.termination_algorithm in \
                TERM_NO_CHANGE_ALG:
            return self.no_change(past_n_evals)
        return 1

    def survival_strategy_selection(self, old_generation, children):
        """ Decide on next generation for survival function.

        old_generation - list of individuals that make up the older generation
        children - list of individuals that make up children for the new generation
        """

        if self.survival_strategy_algorithm in PLUS:
            # (μ + λ)-EA
            return old_generation + children

        if self.survival_strategy_algorithm in COMMA:
            # (μ, λ)-EA
            return children

    def child_creation(self, population, original_board):
        """ Generate child using recombination and mutation.

        population - list of individuals that make up the parents for the children
        original_board -  RxC numpy array representing the game board,
        filled with bulbs, black cells, and light
        """

        children = []
        for _ in range(self.children):
            board = original_board.copy()
            parent_one, parent_two = random.sample(population, 2)

            if self.child_algorithm in ONE_POINT:
                child_solution = self.one_point_crossover(
                    parent_one, parent_two)
            elif self.child_algorithm in UNIFORM:
                child_solution = self.uniform_crossover(
                    parent_one, parent_two)

            child_solution, mutation_rate, penalty_coefficient = self.child_mutation(
                parent_one, parent_two, child_solution, original_board)

            # place child's bulbs to calculate fitness
            for location in child_solution:
                board = lightup.place_bulb(board, location)

            fitness, penalty = self.calculate_fitness(
                board, penalty_coefficient)

            # determine if child should have a mutation rate gene
            kwargs = {'fitness': fitness,
                      'solution': child_solution, 'penalty': penalty}

            if self.self_adaptive_mutation:
                kwargs['mutation_rate'] = mutation_rate

            if self.self_adaptive_penalty:
                kwargs['penalty_coefficient'] = penalty_coefficient

            child = Individual(**kwargs)

            children.append(child)

        return children

    def child_mutation(self, parent_one, parent_two, child_solution, original_board):
        """ Mutates child based on mutation rate that is inherent to parents or a general
        mutation rate.

        If self-adaptive mutation then pick mutation rate from one of the parents
        Otherwise use global mutation rate

        parent_one - individual selected to be a parent of the child
        parent_two - individual selected to be a parent of the child
        child_solution - current solution to be used for the child produced from
            parent recombination
        original_board - original board that will be used for mutation
        """

        # determine which mutation to use
        if self.self_adaptive_mutation:
            if random.randint(0, 1):
                mutation_rate = parent_one.mutation_rate
            else:
                mutation_rate = parent_two.mutation_rate
        else:
            mutation_rate = self.mutation_rate if self.mutation_rate is not None else 1

        if self.self_adaptive_penalty:
            if random.randint(0, 1):
                penalty_coefficient = parent_one.penalty_coefficient
            else:
                penalty_coefficient = parent_two.penalty_coefficient
        else:
            penalty_coefficient = self.penalty_coefficient

        # add in mutation
        rng = random.random()
        if rng <= mutation_rate:
            self.creep_mutation(child_solution, original_board)
            if self.self_adaptive_mutation:
                mutation_rate = self.mutate_mutation_rate(mutation_rate)
            else:
                mutation_rate = self.mutation_rate

            if self.self_adaptive_penalty:
                penalty_coefficient = self.mutate_penalty_coefficient(
                    penalty_coefficient)
            else:
                penalty_coefficient = self.penalty_coefficient

        return child_solution, mutation_rate, penalty_coefficient

    ###########################################################################
    ###################### Recombination / Mutation ###########################
    ###########################################################################

    @staticmethod
    def one_point_crossover(parent_one, parent_two):
        """ Stochastically pick the point at which you crossover in the two parents and
        merge into the child.

        parent_one - individual denoted for parent one
        parent_two - individual denoted for parent two
        """

        val = random.random()
        child_solution = []

        parent_one_scale = round(parent_one.iterations * val)
        parent_two_scale = round(parent_two.iterations * val)
        if random.randint(0, 1):
            child_solution += parent_one.solution[parent_one_scale:]
            child_solution += parent_two.solution[:parent_two_scale]
        else:
            child_solution += parent_one.solution[:parent_one_scale]
            child_solution += parent_two.solution[parent_two_scale:]

        return child_solution

    @staticmethod
    def list_extend(list_in, num_to_extend):
        """ Utility function used to arbitrarily extend a list by n length

        list_in - list to extend
        num_to_extend - amount to extend the list by
        """

        list_out = list_in.copy()
        list_out.extend([0]*num_to_extend)
        return list_out

    def uniform_crossover(self, parent_one, parent_two):
        """ Recombination function that uses uniform crossover."""

        max_iterations = parent_one.iterations if parent_one.iterations > parent_two.iterations\
            else parent_two.iterations

        parent_one_list = self.list_extend(parent_one.solution,
                                           abs(parent_one.iterations - max_iterations))
        parent_two_list = self.list_extend(parent_two.solution,
                                           abs(parent_two.iterations - max_iterations))

        child_list = []
        while not child_list:
            for index in range(max_iterations):
                if random.randint(0, 1):
                    child_list.append(parent_one_list[index])
                else:
                    child_list.append(parent_two_list[index])

            # clear out temp 0 values
            child_list = [x for x in child_list if x != 0]

        return child_list

    def mutate_mutation_rate(self, mutation_rate):
        creep_rate = random.random()
        if random.randint(0, 1):
            mutation_rate += creep_rate
            mutation_rate = min(mutation_rate, 1)
        else:
            mutation_rate -= creep_rate
            mutation_rate = max(mutation_rate, 0)

        return mutation_rate

    def mutate_penalty_coefficient(self, mutation_rate):
        creep_rate = random.randint(0, 10)
        if random.randint(0, 1):
            mutation_rate += creep_rate
            mutation_rate = min(mutation_rate, 100)
        else:
            mutation_rate -= creep_rate
            mutation_rate = max(mutation_rate, 0)

        return mutation_rate

    def creep_mutation(self, solution, board):
        """ Mutation function using creep algorithm.

        Stochastically determines:
            If individual should be mutated
            How many genes should be mutated
            How to much to offset said genes
        """

        iterations = len(solution)

        num_to_mutate = random.randrange(0, iterations)

        for _ in range(num_to_mutate):
            try_again = True
            while try_again:
                choice = random.randrange(0, iterations)
                bulb = solution[choice]

                # move bulb
                if random.randint(0, 1):
                    # move y
                    offset = random.randrange(1, self.shape[1])
                    current_location = bulb[1]
                    new_location = abs(offset - current_location)
                    new_bulb = (new_location, bulb[1])
                else:
                    # move x
                    offset = random.randrange(1, self.shape[0])
                    current_location = bulb[0]
                    new_location = abs(offset - current_location)
                    new_bulb = (bulb[0], new_location)

                if board[new_bulb[0]][new_bulb[1]] in [lightup.NOT_LIT, lightup.LIT]:
                    solution[choice] = bulb
                    try_again = False

    ###########################################################################
    ############################# Logging #####################################
    ###########################################################################

    def log_run_header(self, run_count):
        """Logs current run header."""

        with open(self.log_file, "+a") as file:
            file.write(f"\nRun {run_count}\n")

    def log_best_ind_per_run(self, individuals):
        """ Logs best individual per run. """
        with open(self.log_file[:-4] + "_best_from_gen.log", "+w") as file:
            for individual in individuals:
                file.write(f"{individual.fitness}\n")
        if self.log_1b:
            with open(self.log_file[:-4] + "_best_from_gen_1b.log", "+w") as file:
                for individual in individuals:
                    fitness = individual.fitness if individual.penalty == 0 else 0
                    file.write(f"{fitness}\n")

    def log_generation(self, evals, population):
        """ Logs best individual, and average fitness for current generation.

        evals - current eval count
        population - list of individuals for current generation
        """

        best_individual = max(population)
        avg_fitness = round(sum(population) / len(population), 2)
        with open(self.log_file, '+a') as file:
            file.write(
                f"\t{evals}\t{avg_fitness}\t{best_individual.fitness}\n")

    def log_experiment_config(self, problem_file):
        """ Log configuration information for current experiment.

        problem_file - name of file that is currently being solved
        """

        with open(self.log_file, "a") as file:
            file.write('\nConfiguration Information\n\n')
            file.write(f"\tProblem Instance File Path: {problem_file}\n")
            file.write(f"\tSolution File Path: {self.solution_file}\n")
            file.write(f"\tSeed: {self.seed}\n")
            file.write(
                f"\tIgnore Black Cell Constraints: {self.ignore_black_cells}\n")
            file.write(f"\tNumber of runs: {self.num_of_runs}\n")
            file.write(f"\tMax number of evals: {self.fitness_evals}\n")

            if self.algorithm:
                file.write(f'\tAlgorithm: {self.algorithm}\n')

            else:

                file.write(
                    f'\tSurvival algorithm: {self.survival_algorithm}\n')
                file.write(f'\tParent algorithm: {self.parent_algorithm}\n')
                file.write(
                    f'\tTermination algorithm: {self.termination_algorithm}\n')
                file.write(
                    f'\tSurvival Strategy Algorithm: {self.survival_strategy_algorithm}\n')
                file.write(
                    f'\tConstraint Algorithm: {self.constraint_algorithm}\n')
                if self.penalty_coefficient:
                    file.write(
                        f'\tPenalty Coefficient: {self.penalty_coefficient}\n')
                if self.self_adaptive_mutation:
                    self_mut = 'True'
                else:
                    self_mut = 'False'
                file.write(f'\tSelf-Adaptivity Mutation: {self_mut}\n')
                if self.self_adaptive_penalty:
                    self_pen = 'True'
                else:
                    self_pen = 'False'
                file.write(f'\tSelf-Adaptivity Penalty: {self_pen}\n')
                file.write(f'\tλ: {self.children}\n')
                file.write(f'\tμ: {self.parents}\n')

                if self.tournament_parent:
                    file.write(
                        f'\tTournament size for parent selection {self.tournament_parent}\n')
                if self.tournament_survival:
                    file.write(
                        f'\tTournament size for survival selection {self.tournament_survival}\n')
                if self.n_termination:
                    file.write(
                        f'\tTerminates after {self.n_termination} runs with no improvements\n')

    def log_solution(self, best_individual, problem_filename):
        """ Log best solution out of all runs.

        fitness_evals - highest fitness achieved out of all runs
        best_solution - best solution out of all runs
        problem_filename - problem file that the solution matches to
        """

        # copies problem file as per specifications of the start for solution files
        copyfile(problem_filename, self.solution_file)
        logging.debug("Logging best solution for all runs at %s\n",
                      self.solution_file)
        with open(self.solution_file, "a") as file:
            file.write(f"\n{best_individual.fitness}\n")
            for coordinates in best_individual.solution:
                # add one to offset for it starting at 1
                file.write(
                    f"{coordinates[1]+1} {self.shape[0] - coordinates[0]}\n")

    ###########################################################################
    #################### Initialization Algorithms ############################
    ###########################################################################

    def initialize_population(self, original_board):
        """ Generate an initial μ-population based on a uniform distribution.

        original_board - RxC numpy array representing the game board,
        filled with bulbs, black cells, and light
        """

        initialize_population = []
        for _ in range(self.parents):
            board = original_board.copy()

            fitness, solution, penalty, penalty_coef = self.initialization_selection(
                board)

            kwargs = {'fitness': fitness,
                      'solution': solution, 'penalty': penalty}

            if self.self_adaptive_mutation:
                kwargs['mutation_rate'] = random.random()

            if self.self_adaptive_penalty:
                kwargs['penalty_coefficient'] = penalty_coef

            initialize_population.append(Individual(**kwargs))
        return initialize_population

    def uniform_random(self, board):
        """Random Search solver algorithm. Randomly picks N bulbs to place
        at random open locations across the board.

        board - RxC numpy array representing the game board, filled with bulbs,
        black cells, and light
        """

        # generate list of possible locations to place a bulb
        list_of_locations = np.where(board == lightup.NOT_LIT)
        list_of_locations = list(
            zip(list_of_locations[0], list_of_locations[1]))

        # get number of bulbs to place from [1, NUM_OF_POSSIBLE_LOCATIONS]
        num_of_bulbs_to_place = random.randint(1, len(list_of_locations))

        solution = []
        for _ in range(num_of_bulbs_to_place):
            location = random.choice(list_of_locations)
            list_of_locations.remove(location)
            board = lightup.place_bulb(board, location)
            solution.append(location)

        if self.self_adaptive_penalty:
            penalty_coef = random.random()
        else:
            penalty_coef = self.penalty_coefficient
        fitness, penalty = self.calculate_fitness(board, penalty_coef)

        return (fitness, solution, penalty, penalty_coef)

    def uniform_random_with_forced_validity(self, original_board):
        """Random Search solver algorithm. Randomly picks N bulbs to place
        at random open locations across the board. First shrinks search space by
        placing bulbs around black cells that have unique solutions.

        board - RxC numpy array representing the game board, filled with bulbs,
        black cells, and light

        """
        # place bulbs around black cells and ensure non intersection
        board = original_board.copy()

        zero_black_cell = np.where(board == 0)
        list_of_zero_black_cell = list(
            zip(zero_black_cell[0], zero_black_cell[1]))

        # shrinks space to avoid spots around black cells with 0
        invalid_spots = set()
        for cell in list_of_zero_black_cell:
            possible_spots = lightup.get_spots_around_cell(cell, self.shape)
            invalid_spots.update(possible_spots)

        solutions = []

        change = True

        satisfied_cells = []
        while change:
            change = False
            for value in reversed(range(1, 5)):
                locations = np.where(board == value)
                list_of_black_cells = tuple(zip(locations[0], locations[1]))
                invalid_spots.update(list_of_black_cells)

                for cell in list_of_black_cells:
                    if cell in satisfied_cells:

                        continue
                    possible_spots = lightup.get_spots_around_cell(
                        cell, self.shape)

                    # if there is 4 in the black cell there is only one solution and its all around
                    # the cell
                    if value == 4:
                        for spot in possible_spots:
                            lightup.place_bulb(board, spot)
                        continue

                    possible_combos = list(
                        itertools.combinations(possible_spots, value))

                    # trim invalid spots out
                    combos = []
                    for combo in possible_combos:
                        valid = True
                        for choice in combo:
                            if choice in invalid_spots or \
                                    board[choice[0]][choice[1]] != lightup.NOT_LIT:
                                valid = False
                                break

                        if valid:
                            combos.append(combo)

                    # only one unique spot for this black cell
                    if len(combos) == 1:
                        solutions.append(combos[0])
                        for bulb in combos[0]:
                            lightup.place_bulb(board, bulb)
                        change = True
                        satisfied_cells.append(cell)

        return board

    ###########################################################################
    ####################### Constraint Algorithms #############################
    ###########################################################################

    def calculate_fitness(self, board, penalty_coef):
        """ Calculates fitness of current board.

        board - RxC numpy array representing the game board, filled with bulbs,
        black cells, and light
        """
        fitness = lightup.calculate_completion(board)
        black_cells = lightup.check_black_cells(board, self.ignore_black_cells)
        intersections = lightup.check_intersections(board)
        fitness_prime = fitness

        if self.constraint_algorithm in CON_PENALTY:
            if penalty_coef is None:
                penalty_coef = self.penalty_coefficient
            fitness_prime = self.penalty_function(
                fitness, black_cells, intersections, penalty_coef)

        penalty = fitness - fitness_prime
        return fitness_prime, penalty

    def penalty_function(self, fitness, black_cells, intersections, penalty_coef):
        """ Penalizes current individual based on the amount of intersecting rays
        and black cells that are not constrained.

        f' = f - p*(black_cells + intersections)

        where f is the original fitness
        where f' is the new fitness
        where p is the penalty coefficient
        """

        penalty = 0
        for expected, actual_list in black_cells.items():
            for actual in actual_list:
                penalty += abs(expected - actual)

        for section in intersections.values():
            for intersection in section:
                penalty += intersection

        fitness -= penalty*penalty_coef
        return fitness

    ###########################################################################
    #################### Parent Selection Algorithms ##########################
    ###########################################################################

    def uniform_random_parent(self, individuals):
        """ Selects parents randomly with a uniform distribution

        individuals - list of Individual objects
        """

        mating_pool = random.choices(individuals, k=self.children*2)
        return mating_pool

    def stochastic_uniform_sampling(self, individuals):
        """ Selects parents based on fitness

        individuals - list of Individual objects
        """
        fitness_sum = sum(individuals)
        if fitness_sum == 0:
            return random.choices(individuals, k=self.children*2)

        probs = [individual.fitness /
                 fitness_sum for individual in individuals]

        for i in range(1, len(probs)):
            probs[i] = probs[i] + probs[i-1]

        mating_pool = []

        rng = random.random()/(self.children*2)

        current_member = 0
        i = 0

        while current_member < (self.children*2
                                ):
            while rng < probs[i]:
                mating_pool.append(individuals[i])
                rng += 1/(self.children*2)
                current_member += 1
            i += 1

        return mating_pool

    def fitness_proportional_selection(self, individuals):
        """ Selects parents based on fitness probability.

        individuals - list of Individual objects
        """

        fitness_sum = sum(individuals)
        if fitness_sum == 0:
            return random.choices(individuals, k=self.children*2)

        probs = [individual.fitness /
                 fitness_sum for individual in individuals]

        return random.choices(individuals, probs, k=self.children*2)

    def tournament_selection_parent(self, individuals):
        """ Selects parents using a tournament based system. Grabs k individuals
        and selects the best individual out of that set.

        For parent selection we will be using replacement

        individuals: list of Individual objects
        """

        chosen_parents = []
        for _ in range(self.children*2):

            selection = random.choices(individuals, k=self.tournament_parent)

            selection_sorted = sorted(selection)
            chosen_parents.append(selection_sorted.pop())
        return chosen_parents

    ###########################################################################
    ################## Survival Selection Algorithms ##########################
    ###########################################################################

    def fitness_proportional_selection_survival(self, individuals):
        """ Selects parents based on fitness probability without replacement.

        individuals - list of Individual objects
        """

        fitness_sum = sum(individuals)
        if fitness_sum == 0:
            return random.choices(individuals, k=self.children*2)

        probs = [individual.fitness /
                 fitness_sum for individual in individuals]

        return list(np.random.choice(individuals, p=probs, size=self.children*2, replace=False))

    def uniform_random_survival(self, individuals):
        """ Selects parents randomly without replacement with a uniform distribution

        individuals - list of Individual objects
        """

        mating_pool = random.sample(individuals, k=self.parents)
        return mating_pool

    def truncation(self, individuals):
        """ Selects μ best individuals

        individuals: list of Individual objects
        """
        return sorted(individuals, reverse=True)[: self.parents]

    def tournament_selection_survival(self, individuals):
        """ Selects parents using a tournament based system. Grabs k individuals
        and selects the best individual out of that set.

        For survival selection we will not be using replacement

        individuals: list of Individual objects
        """

        chosen = []
        for _ in range(self.parents):

            selection = random.sample(individuals, k=self.tournament_survival)

            selection_sorted = sorted(selection)
            chosen.append(selection_sorted.pop())
        return chosen

    ###########################################################################
    ###################### Termination Algorithms #############################
    ###########################################################################

    def num_of_evals(self, eval_num):
        """ Stop running if we have reached the max eval number.

        eval_num - current evaluation iteration
        """

        return self.fitness_evals > eval_num

    def no_change(self, past_n_evals):
        """ Stop running if for the past n runs fitness has not changed

        past_n_evals - past n evals with no change
        """

        return self.n_termination > past_n_evals
