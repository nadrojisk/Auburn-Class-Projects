""" Module that implements a solver object for completing the lightup problem. """
import itertools
from shutil import copyfile
import json
import random
import time
import lightup
import numpy as np
from individual import Individual


class Solver:
    """Solver object for the LightUp problem.

    config_filename -- path to the config file
    verbose -- boolean to determine if verbose output should be printed
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
            if self.seed == 'None':
                self.seed = None

            self.ignore_black_cells = config.get('ignore_black_cells')
            if self.ignore_black_cells is None:
                self.ignore_black_cells = False

            self.force_validity = config.get('force_validity')
            self.children = config.get('children')  # λ
            self.parents = config.get('parents')    # μ

            self.parent_algorithm = config.get('parent_alg')
            self.survival_algorithm = config.get('survival_alg')
            self.termination_algorithm = config.get('termination_alg')
            self.initialization_algorithm = config.get('initialization_alg')
            self.child_algorithm = config.get('child_alg')
            # setting K for tournament
            self.tournament_parent = config.get('t_parent')
            self.tournament_survival = config.get('t_survival')

            # setting for FPS
            self.windowed = config.get('windowed')

            # n runs with no change until termination
            self.n_termination = config.get('n')

            self.evals = []
            self.shape = []
            self.verbose = verbose

    def set_seed(self):
        """Sets random seed value based on object seed variable."""

        if self.seed is None:
            self.seed = time.time()
        random.seed(self.seed)

    def run(self, problem_filename):
        """Runs algorithm to attempt to solve the current problem

        problem_filename -- path to the problem file
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

        if self.verbose:
            print("Running Random Search Algorithm")
        num_of_runs = range(self.num_of_runs)

        # self.log_experiment_config(problem_filename)

        max_ind_of_experiment = None
        best_runs = []
        for _ in num_of_runs:

            max_ind_of_run = None
            population = []
            for _ in range(self.fitness_evals):

                board = original_board.copy()
                runtime, iterations, fitness, solution = self.uniform_random(
                    board)
                population.append(Individual(
                    fitness, solution=solution, iterations=iterations, runtime=runtime))

                max_ind_of_generation = max(population)

                if max_ind_of_experiment is None or max_ind_of_experiment < max_ind_of_generation:
                    max_ind_of_experiment = max_ind_of_generation

                if max_ind_of_run is None or max_ind_of_run < max_ind_of_generation:
                    max_ind_of_run = max_ind_of_generation
            best_runs.append(max_ind_of_run)
        self.log_best_ind_oer_run(best_runs)

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

        if self.verbose:
            print("Running EA")

        num_of_runs = range(self.num_of_runs)

        max_ind_of_experiment = None
        past_evals_with_no_change = 0
        best_runs = []
        for run in num_of_runs:

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
                population = self.survival_selection(population, children)

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
        self.log_best_ind_oer_run(best_runs)
        self.log_solution(max_ind_of_experiment, problem_filename)

    ###########################################################################
    ###################### Algorithm Selection ################################
    ###########################################################################

    def initialization_selection(self, original_board):
        """ Generate μ-individuals for intiail generation based on chosen algorithm

        original_board - RxC numpy array representing the game board,
        filled with bulbs, black cells, and light
        """
        try:
            if self.initialization_algorithm.lower() in ['validity forced']:
                board = self.uniform_random_with_forced_validity(
                    original_board)
                original_board = board
            return self.uniform_random(original_board)
        except AttributeError:
            return self.uniform_random(original_board)

    def parent_selection(self, population):
        """ Select 2λ-parents for next generation based on chosen algorithm since
        I have chosen to get with a 2->1 reproduction operator (2 parents, 1 child)

        population - list of individuals to be used to create the next generation
        """

        try:
            if self.parent_algorithm.lower() in \
                    ['fitness proportional selection', 'fps']:
                population = self.fitness_proportional_selection(
                    population)
            elif self.parent_algorithm.lower() in \
                    ['k-tournament selection with replacement', 'tournament']:
                population = self.tournament_selection_parent(population)
            elif self.parent_algorithm.lower() in ['sus']:
                population = self.stochastic_uniform_sampling(population)
        except AttributeError:
            population = self.fitness_proportional_selection(population)
        return population

    def survival_selection(self, population, children):
        """ Selects μ-individuals to survive into the next generation based on
        a chosen algorithm.

        population - list of old individuals from prior generation
        children - list of new individuals from new generation
        """
        population += children

        try:
            if self.survival_algorithm.lower() in ['truncation']:
                population = self.truncation(population)
            elif self.survival_algorithm.lower() in\
                    ['k-tournament selection without replacement', 'tournament']:
                population = self.tournament_selection_survival(population)
        except AttributeError:
            population = self.truncation(population)
        return population

    def termination_selection(self, evals, past_n_evals):
        """ Determines whether to end the current run based on termination criteria.

        evals - number of current evals
        past_n_fitnesses - list of past n fitnesses
        max_ind - best individual object of current generation
        """
        try:
            if self.termination_algorithm.lower() in \
                    ['number of evals till termination', 'num of evals']:
                return self.num_of_evals(evals)
            if self.termination_algorithm.lower() in \
                    ['no change in fitness for n evals', 'n evals']:
                return self.no_change(past_n_evals)
            return 1
        except AttributeError:
            return self.num_of_evals(evals)

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

            try:
                if self.child_algorithm.lower() in ['one point crossover']:
                    child_solution = self.one_point_crossover(
                        parent_one, parent_two)
                elif self.child_algorithm.lower() in ['uniform']:
                    child_solution = self.uniform_crossover(
                        parent_one, parent_two)
            except AttributeError:
                child_solution = self.one_point_crossover(
                    parent_one, parent_two)

            for location in child_solution:
                board = lightup.place_bulb(board, location)
            fitness = lightup.calculate_fitness(board, self.ignore_black_cells)

            child = Individual(
                fitness, solution=child_solution, iterations=len(child_solution))
            # add in mutation
            self.creep_mutation(child, original_board)
            children.append(child)

        return children

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

    def creep_mutation(self, individual, board):
        """ Mutation function using creep algorithm.

        Stochastically determines:
            If individual should be mutated
            How many genes should be mutated
            How to much to offset said genes
        """

        if random.randint(0, 1):

            num_to_mutate = random.randrange(0, individual.iterations)

            for _ in range(num_to_mutate):
                try_again = True
                while try_again:
                    choice = random.randrange(0, individual.iterations)
                    bulb = individual.solution[choice]

                    # move bulb
                    if random.randint(0, 1):
                        # move y
                        offset = random.randrange(1, self.shape[1])
                        current_location = bulb[1]
                        new_location = abs(offset - current_location)
                        bulb = (new_location, bulb[1])
                    else:
                        # move x
                        offset = random.randrange(1, self.shape[0])
                        current_location = bulb[0]
                        new_location = abs(offset - current_location)
                        bulb = (bulb[0], new_location)

                    if board[bulb[0]][bulb[1]] == lightup.NOT_LIT:
                        individual.solution[choice] = bulb
                        try_again = False

    ###########################################################################
    ############################# Logging #####################################
    ###########################################################################

    def log_run_header(self, run_count):
        """Logs current run header."""

        with open(self.log_file, "+a") as file:
            file.write(f"\nRun {run_count}\n")

    def log_best_ind_oer_run(self, individuals):
        """ Logs best individual per run. """
        with open(self.log_file[:-4] + "_best_from_gen.log", "+w") as file:
            for individual in individuals:
                file.write(f"{individual.fitness}\t{individual.name}\n")

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
                file.write(f'\tλ: {self.children}\n')
                file.write(f'\tμ: {self.parents}\n')

                if self.windowed:
                    file.write(f"\tWindowed for FPS: {self.windowed}\n")
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

        fitness_evals -- highest fitness achieved out of all runs
        best_solution -- best solution out of all runs
        problem_filename -- problem file that the solution matches to
        """

        # copies problem file as per specifications of the start for solution files
        copyfile(problem_filename, self.solution_file)
        if self.verbose:
            print(
                f"Logging best solution for all runs at {self.solution_file}\n")
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

            runtime, iterations, fitness, solution = self.initialization_selection(
                board)
            initialize_population.append(Individual(
                fitness, solution=solution, iterations=iterations, runtime=runtime))
        return initialize_population

    def uniform_random(self, board):
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

        return (time.time()-start, iterations, fitness, solution)

    def uniform_random_with_forced_validity(self, original_board):
        """Random Search solver algorithm. Randomly picks N bulbs to place
        at random open locations across the board. First shrinks search space by
        placing bulbs around black cells that have unique solutions.

        board -- RxC numpy array representing the game board, filled with bulbs,
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
    #################### Parent Selection Algorithms ##########################
    ###########################################################################

    def stochastic_uniform_sampling(self, individuals):
        """ Selects parents randomly

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

        if self.windowed:
            # f'(x) = f(x) - β + 1; where β = min(fitness)
            min_fit = min(individuals).fitness
            for individual in individuals:
                individual.windowed(min_fit)

        fitness_sum = sum(individuals)
        if fitness_sum == 0:
            return random.choices(individuals, k=self.children*2)

        probs = [individual.fitness /
                 fitness_sum for individual in individuals]

        self.cleanup(individuals)

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

    def truncation(self, individuals):
        """ Selects μ best individuals

        individuals: list of Individual objects
        """
        return sorted(individuals, reverse=True)[:self.parents]

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

    @ staticmethod
    def cleanup(individuals):
        """ Static method for cleaning up individuals after running fps.

        individuals - list of individual objects
        """
        for individual in individuals:
            individual.cleanup()
