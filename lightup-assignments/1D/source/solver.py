""" Module that implements a solver object for completing the lightup problem. """
import collections
from pathlib import Path
import itertools
from shutil import copyfile
import json
import random
import time
import logging
import scipy.spatial
import lightup
import numpy as np
from individual import Individual
import tqdm


class MyException(Exception):
    """ custom exception to raise on issues """


# Survival Strategy Algorithms
PLUS = ['plus']
COMMA = ['comma', 'generation']
SURV_STRAT_ALGS = PLUS + COMMA


class ParetoFront:
    def __init__(self, individuals):
        self.individuals = individuals

    @classmethod
    def pareto_front_from_dict(cls, front_dict):
        return [cls(front) for front in front_dict.values()]

    def __lt__(self, other):
        total_this_domination_count = 0
        total_other_domination_count = 0
        for other_sol in other.individuals:
            this_domination_count = 0
            other_domination_count = 0
            for solution in self.individuals:
                if solution > other_sol:
                    this_domination_count += 1
                elif other_sol > solution:
                    other_domination_count += 1
            total_other_domination_count += other_domination_count
            total_this_domination_count += this_domination_count

        return (total_this_domination_count / len(self.individuals)) < \
            (total_other_domination_count / len(other.individuals))


class Solver:
    """Solver object for the LightUp problem.

    config_filename - path to the config file
    verbose - boolean to determine if verbose output should be printed
    """

    def __init__(self, config_filename, verbose=False):

        # following lines simply setup dictionary of key value pairs that allow the program
        # to more dynamically select which algorithm to run

        # Survival Selection Algorithms
        self.survival_truncation = {'truncation': self.truncation}
        self.survival_tournament = {
            'k-tournament selection without replacement': self.tournament_selection_survival,
            'tournament': self.tournament_selection_survival}
        self.survival_uniform = {'uniform': self.uniform_random_survival}
        self.survival_fps = {
            'fps': self.fitness_proportional_selection_survival}
        self.survival_algs = {**self.survival_uniform,
                              **self.survival_fps,
                              **self.survival_tournament,
                              **self.survival_truncation}

        # Initialization Algorithms
        self.initialization_validity_forced = {
            'validity forced': self.uniform_random_with_forced_validity}
        self.initialization_vanilla = {'vanilla': self.uniform_random}
        self.initialization_algs = {**self.initialization_validity_forced,
                                    **self.initialization_vanilla}

        # Parent Selection Algorithms
        self.parent_fps = {'fitness proportional selection': self.fitness_proportional_selection,
                           'fps': self.fitness_proportional_selection}
        self.parent_tournament = {
            'k-tournament selection with replacement': self.tournament_selection_parent,
            'tournament': self.tournament_selection_parent}
        self.parent_sus = {'sus': self.stochastic_uniform_sampling}
        self.parent_uniform = {'uniform': self.uniform_random_parent}
        self.parent_algs = {**self.parent_fps,
                            **self.parent_tournament,
                            **self.parent_sus,
                            **self.parent_uniform}

        # Recombination Algorithms
        self.recombination_one_point = {
            'one point crossover': self.one_point_crossover}
        self.recombination_uniform = {'uniform': self.uniform_crossover}
        self.recombination_algs = {**self.recombination_one_point,
                                   **self.recombination_uniform}

        # Termination Algorithms
        self.termination_total_eval = {
            'number of evals till termination': self.num_of_evals,
            'num of evals': self.num_of_evals}
        self.termination_no_change = {
            'no change in fitness for n evals': self.no_change,
            'n evals': self.no_change}
        self.termination_algs = {**self.termination_total_eval,
                                 **self.termination_no_change}

        # Diversity Algorithms
        self.diversity_crowding = {'crowding': self.crowding}
        self.diversity_sharing = {'sharing': self.fitness_sharing}
        self.diversity_vanilla = {'vanilla': self.vanilla}
        self.diversity_algs = {
            **self.diversity_crowding, **self.diversity_sharing, **self.diversity_vanilla}

        # parses passed config for relevant information

        self.config = config_filename
        with open(config_filename) as file:
            config = json.load(file)

            self.log_file = config.get('log_file')
            self.solution_file = config.get('solution_file')

            self.max_evals = config.get('fitness_evals')
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

            self.sigma = config.get('sigma', 15)
            self.diversity_algorithm = config.get('diversity_algorithm')
            self.bulb_objective = config.get('bulb_objective')
            try:
                self.parent_selection_alg = config.get('parent_alg').lower()
                self.survival_selection_alg = config.get(
                    'survival_alg').lower()
                self.termination_alg = config.get(
                    'termination_alg').lower()
                self.initialization_alg = config.get(
                    'initialization_alg').lower()
                self.recombination_alg = config.get('child_alg').lower()
                self.survival_strategy_alg = config.get(
                    'survival_strategy_alg').lower()
            except AttributeError as error:
                print("Error: Did not provide algorithm")
                raise AttributeError from error

            self.mutation_rate = config.get('mutation_rate')

            # setting K for tournament
            self.tournament_parent = config.get('t_parent')
            self.tournament_survival = config.get('t_survival')

            # n runs with no change until termination
            self.n_termination = config.get('n')

            self.shape = []
            self.verbose = verbose

            if self.verbose:
                logging.basicConfig(level=logging.DEBUG,
                                    format='%(message)s')

            # ensure all passed params are valid and legal otherwise quit
            self.error_checking()

    ###########################################################################
    ############################# Solver ######################################
    ###########################################################################

    def run(self, problem_filename):
        """Runs algorithm to attempt to solve the current problem

        problem_filename - path to the problem file
        """
        start_time = time.time()
        path = '/'.join(self.log_file.split('/')[:-1])
        Path(path).mkdir(parents=True, exist_ok=True)
        with open(self.log_file, "+w") as file:
            file.write("Result Log\n\n")

        self.set_seed()
        original_board = lightup.create_board(problem_filename)
        self.shape = original_board.shape

        self.evolutionary_algorithm(original_board, problem_filename)

        with open(self.log_file, '+a') as file:
            file.write(f"Runtime: {time.time() - start_time}\n")

    def dom_fronts(self, fronts):
        fronts = ParetoFront.pareto_front_from_dict(fronts)
        return sorted(fronts).pop()

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
        best_front = None
        for run in tqdm.tqdm(num_of_runs):

            self.log_run_header(run + 1)

            population = self.initialize_population(original_board)
            eval_counter = len(population)
            population = self.calculate_moea_fitness(population)

            max_ind_of_generation = max(population)
            if max_ind_of_experiment is None:
                max_ind_of_experiment = max_ind_of_generation

            max_ind_of_run = max_ind_of_generation

            self.log_generation(eval_counter, population)

            keep_going = True
            while keep_going:

                parents = self.parent_selection(population)

                children = self.child_selection(parents, original_board)
                eval_counter += len(children)

                population = self.survival_strategy_selection(
                    population, children)
                population = self.calculate_moea_fitness(population)
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

            fronts = self.split_on_pareto_front(population)
            dominating_front = self.dom_fronts(fronts)

            if best_front is None or best_front < dominating_front:
                best_front = dominating_front

        self.log_best_ind_per_run(best_runs)

        self.log_solution(best_front, problem_filename)

    ###########################################################################
    ###################### Algorithm Selection ################################
    ###########################################################################

    def initialization_selection(self, original_board):
        """ Generate μ - individuals for intiail generation based on chosen algorithm

        original_board - RxC numpy array representing the game board,
        filled with bulbs, black cells, and light
        """
        return self.initialization_algs[self.initialization_alg](original_board)

    def parent_selection(self, population):
        """ Select 2λ - parents for next generation based on chosen algorithm since
        I have chosen to get with a 2 -> 1 reproduction operator(2 parents, 1 child)

        population - list of individuals to be used to create the next generation
        """
        population = self.parent_algs[self.parent_selection_alg](population)
        return population

    def survival_selection(self, population):
        """ Selects μ - individuals to survive into the next generation based on
        a chosen algorithm.

        population - list of old individuals from prior generation
        """

        population = self.survival_algs[self.survival_selection_alg](
            population)
        return population

    def termination_selection(self, evals, past_n_evals):
        """ Determines whether to end the current run based on termination criteria.

        evals - number of current evals
        past_n_fitnesses - list of past n fitnesses
        max_ind - best individual object of current generation
        """

        terminate = self.termination_algs[self.termination_alg]
        return terminate(eval_num=evals, past_n_evals=past_n_evals)

    def survival_strategy_selection(self, old_generation, children):
        """ Decide on next generation for survival function.

        old_generation - list of individuals that make up the older generation
        children - list of individuals that make up children for the new generation
        """

        if self.survival_strategy_alg in PLUS:
            # (μ + λ)-EA
            return old_generation + children

        if self.survival_strategy_alg in COMMA:
            # (μ, λ)-EA
            return children

    def child_selection(self, population, original_board):
        """ Generate child using recombination and mutation.

        population - list of individuals that make up the parents for the children
        original_board - RxC numpy array representing the game board,
        filled with bulbs, black cells, and light
        """

        children = []
        for _ in range(self.children):
            board = original_board.copy()
            parent_one, parent_two = random.sample(population, 2)

            child_solution = self.recombination_algs[self.recombination_alg](
                parent_one, parent_two)

            child_solution = self.child_mutation(
                child_solution, original_board)

            # place child's bulbs to calculate fitness
            for location in child_solution:
                board = lightup.place_bulb(board, location)

            fitness, black_cells, intersections = self.calculate_fitness(board)

            kwargs = {'lit': fitness, 'solution': child_solution,
                      'black_cell_violations': black_cells, 'bulb_violations': intersections}
            if self.bulb_objective:
                kwargs['bulbs'] = len(child_solution)

            children.append(Individual(**kwargs))

        return children

    ###########################################################################
    #################### Initialization Algorithms ############################
    ###########################################################################

    def initialize_population(self, original_board):
        """ Generate an initial μ - population based on a uniform distribution.

        original_board - RxC numpy array representing the game board,
        filled with bulbs, black cells, and light
        """

        initialize_population = []
        for _ in range(self.parents):
            board = original_board.copy()

            fitness, solution, black_cells, intersections = self.initialization_selection(
                board)
            kwargs = {'lit': fitness, 'solution': solution,
                      'black_cell_violations': black_cells, 'bulb_violations': intersections}
            if self.bulb_objective:
                kwargs['bulbs'] = len(solution)

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

        fitness, black_cells, intersections = self.calculate_fitness(board)

        return (fitness, solution, black_cells, intersections)

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

        return self.uniform_random(board)

    ###########################################################################
    ####################### Constraint Algorithms #############################
    ###########################################################################

    def calculate_fitness(self, board):
        """ Calculates fitness of current board.

        board - RxC numpy array representing the game board, filled with bulbs,
        black cells, and light
        """
        fitness = lightup.calculate_completion(board)
        black_cells = lightup.check_black_cells(board, self.ignore_black_cells)
        intersections = lightup.check_intersections(board)

        black_cell_violations, intersection_violations = self.calculate_violations(
            black_cells, intersections)
        return fitness, black_cell_violations, intersection_violations

    def calculate_violations(self, black_cells, intersections):
        """ Penalizes current individual based on the amount of intersecting rays
        and black cells that are not constrained.

        f' = f - p * (black_cells + intersections)

        where f is the original fitness
        where f' is the new fitness
        where p is the penalty coefficient
        """

        black_cell_violations = 0
        for expected, actual_list in black_cells.items():
            for actual in actual_list:
                black_cell_violations += abs(expected - actual)

        intersection_violations = 0
        for section in intersections.values():
            intersection_violations += sum(section)

        return black_cell_violations, intersection_violations

    ###########################################################################
    #################### Parent Selection Algorithms ##########################
    ###########################################################################

    def uniform_random_parent(self, individuals):
        """ Selects parents randomly with a uniform distribution

        individuals - list of Individual objects
        """

        mating_pool = random.choices(individuals, k=self.children * 2)
        return mating_pool

    def stochastic_uniform_sampling(self, individuals):
        """ Selects parents based on fitness

        individuals - list of Individual objects
        """
        fitness_sum = sum(individuals)
        if fitness_sum == 0:
            return random.choices(individuals, k=self.children * 2)

        probs = [individual.fitness /
                 fitness_sum for individual in individuals]

        for i in range(1, len(probs)):
            probs[i] = probs[i] + probs[i - 1]

        mating_pool = []

        rng = random.random() / (self.children * 2)

        current_member = 0
        i = 0

        while current_member < (self.children * 2
                                ):
            while rng < probs[i]:
                mating_pool.append(individuals[i])
                rng += 1 / (self.children * 2)
                current_member += 1
            i += 1

        return mating_pool

    def fitness_proportional_selection(self, individuals):
        """ Selects parents based on fitness probability.

        individuals - list of Individual objects
        """

        fitness_sum = sum(individuals)
        if fitness_sum == 0:
            return random.choices(individuals, k=self.children * 2)

        probs = [individual.fitness /
                 fitness_sum for individual in individuals]

        return random.choices(individuals, probs, k=self.children * 2)

    def tournament_selection_parent(self, individuals):
        """ Selects parents using a tournament based system. Grabs k individuals
        and selects the best individual out of that set.

        For parent selection we will be using replacement

        individuals: list of Individual objects
        """

        chosen_parents = []
        for _ in range(self.children * 2):

            selection = random.choices(individuals, k=self.tournament_parent)

            selection_sorted = sorted(selection)
            chosen_parents.append(selection_sorted.pop())
        return chosen_parents

    ###########################################################################
    ###################### Recombination / Mutation ###########################
    ###########################################################################

    @ staticmethod
    def one_point_crossover(parent_one, parent_two):
        """ Stochastically pick the point at which you crossover in the two parents and
        merge into the child.

        parent_one - individual denoted for parent one
        parent_two - individual denoted for parent two
        """

        val = random.random()
        child_solution = []

        parent_one_scale = round(len(parent_one.solution) * val)
        parent_two_scale = round(len(parent_two.solution) * val)
        if random.randint(0, 1):
            child_solution += parent_one.solution[parent_one_scale:]
            child_solution += parent_two.solution[:parent_two_scale]
        else:
            child_solution += parent_one.solution[:parent_one_scale]
            child_solution += parent_two.solution[parent_two_scale:]

        return child_solution

    def uniform_crossover(self, parent_one, parent_two):
        """ Recombination function that uses uniform crossover."""

        parent_one_length = len(parent_one.solutions)
        parent_two_length = len(parent_two.solutions)
        max_iterations = parent_one_length if parent_one_length > parent_two_length\
            else parent_two_length

        parent_one_list = self.list_extend(parent_one.solution,
                                           abs(parent_one_length - max_iterations))
        parent_two_list = self.list_extend(parent_two.solution,
                                           abs(parent_two_length - max_iterations))

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

    def child_mutation(self, child_solution, original_board):
        """ Mutates child based on mutation rate that is inherent to parents or a general
        mutation rate.

        If self - adaptive mutation then pick mutation rate from one of the parents
        Otherwise use global mutation rate

        parent_one - individual selected to be a parent of the child
        parent_two - individual selected to be a parent of the child
        child_solution - current solution to be used for the child produced from
            parent recombination
        original_board - original board that will be used for mutation
        """

        mutation_rate = self.mutation_rate if self.mutation_rate is not None else 1

        # mutate solution
        rng = random.random()
        if rng <= mutation_rate:
            self.creep_mutation(child_solution, original_board)

        return child_solution

    ###########################################################################
    ######################### Diversity Algorithms ############################
    ###########################################################################

    def sh_func(self, distance):
        """ Sharing function if distance is less than sigma calculate value otherwise return 0."""
        if distance < self.sigma:
            return 1 - (distance / self.sigma)
        return 0

    def update_fitness(self, population, modified_fitness):
        """ Takes in existing population and updates with new fitness """
        for individual in population:
            individual.fitness += modified_fitness[individual.name]
        return population

    def fitness_sharing(self, population):
        """ Calculates fitness sharing for a specific individual apart of a population.

        Formula: f'(i) = 0.5 / sum(sh(d(i, j)), j < μ) + 1

        Note: adding the + 1 ensures the fitness doesn't become a level higher than it
        was when it started

        0.5 is tunable between 0 and 1
        """
        modified_fitness = {}
        for current in population:
            sh_vals = []
            for individual in population:

                # skip current individual from population
                if current.name == individual.name:
                    continue

                # generate coordinates used to calculate euclidean distance
                point_a = (current.lit, current.black_cell_violations,
                           current.bulb_violations)
                point_b = (individual.lit, individual.black_cell_violations,
                           individual.bulb_violations)

                distance = scipy.spatial.distance.euclidean(point_a, point_b)
                sh_vals.append(self.sh_func(distance))

            sum_sh = sum(sh_vals)
            fitness = 0.5 / ((sum_sh if sum_sh else 1) + 1)
            modified_fitness[current.name] = fitness
        return modified_fitness

    @staticmethod
    def split_on_pareto_front(data):
        """ Takes in list and splits it into sublist on pareto fronts"""
        out = collections.defaultdict(list)
        for value in data:
            out[value.fitness].append(value)
        return out

    @staticmethod
    def crowding_lit(individuals, distance):
        """ Calculates crowding for subobjective percentage lit """
        max_lit = max([
            individual.lit for individual in individuals])
        min_lit = min([
            individual.lit for individual in individuals])

        sorted_on_lit = sorted(individuals,
                               key=lambda ind: ind.lit)

        distance[sorted_on_lit[0].name] = 1000
        distance[sorted_on_lit[-1].name] = 1000

        for index in range(1, len(sorted_on_lit) - 1):
            current = sorted_on_lit[index]
            next_individual = sorted_on_lit[index + 1]
            prior_individual = sorted_on_lit[index - 1]
            try:
                distance[current.name] += (next_individual.lit - prior_individual.lit) / (
                    max_lit - min_lit)
            except ZeroDivisionError:
                distance[current.name] += 0
        return distance

    @staticmethod
    def crowding_black_cell(individuals, distance):
        """ Calculates crowding for subobjective black cell violations """
        max_black_cell_violation = max([
            individual.black_cell_violations for individual in individuals])
        min_black_cell_violation = min([
            individual.black_cell_violations for individual in individuals])

        sorted_on_black_cells = sorted(individuals, reverse=False,
                                       key=lambda ind: ind.black_cell_violations)

        distance[sorted_on_black_cells[0].name] = 1000
        distance[sorted_on_black_cells[-1].name] = 1000

        for index in range(2, len(sorted_on_black_cells) - 1):
            current = sorted_on_black_cells[index]
            next_individual = sorted_on_black_cells[index + 1]
            prior_individual = sorted_on_black_cells[index - 1]
            try:
                distance[current.name] += (next_individual.black_cell_violations -
                                           prior_individual.black_cell_violations) / (
                    max_black_cell_violation - min_black_cell_violation)
            except ZeroDivisionError:
                distance[current.name] += 0
        return distance

    @staticmethod
    def crowding_bulb_violations(individuals, distance):
        """ Calculates crowding for subobjective bulb intersection violations """
        max_bulb_violation = max([
            individual.bulb_violations for individual in individuals])
        min_bulb_violation = min([
            individual.bulb_violations for individual in individuals])

        sorted_on_bulb_violations = sorted(individuals, reverse=False,
                                           key=lambda ind: ind.bulb_violations)

        distance[sorted_on_bulb_violations[0].name] = 1000
        distance[sorted_on_bulb_violations[-1].name] = 1000

        for index in range(2, len(sorted_on_bulb_violations) - 1):
            current = sorted_on_bulb_violations[index]
            next_individual = sorted_on_bulb_violations[index + 1]
            prior_individual = sorted_on_bulb_violations[index - 1]
            try:
                distance[current.name] += \
                    (next_individual.bulb_violations - prior_individual.bulb_violations) / \
                    (max_bulb_violation - min_bulb_violation)
            except ZeroDivisionError:
                distance[current.name] += 0
        return distance

    @staticmethod
    def normalize_data(distance, out_distances):
        """ normalizes data between 0 and 1 / val """

        def normalize(data, val):
            # actual function that normalizes data
            # called twice as we want to normalize the non inf values between 0 and some value
            # infinite between some value and .99
            if data:
                # return {name: value / (val * max(data.values())) for name, value in data.items()}

                out = {}
                for name, value in data.items():
                    denom = (val * max(data.values()))
                    if denom:
                        out[name] = value / denom
                    else:
                        out[name] = 0
                return out
            return {}

        # split distances between inf and non inf
        no_inf_distances = {name: value for name,
                            value in distance.items() if value < 1000}
        inf_distances = {name: value for name,
                         value in distance.items() if value >= 1000}

        normalized_no_inf = normalize(no_inf_distances, 2)
        normalized_inf = normalize(inf_distances, 1.0101010101010102)
        out_distances = {**out_distances, **
                         normalized_no_inf, **normalized_inf}
        return out_distances

    def crowding(self, population):
        """ Crowding implementation to make a population more diverse.

        First splits the population based on its ranks.
        Iterates through each rank and performs crowding on each individual in a rank
        """

        fronts = self.split_on_pareto_front(population)
        out_distances = {}
        for individuals in fronts.values():
            distance = {individual.name: 0 for individual in individuals}

            # Lit Subobjective
            distance = self.crowding_lit(individuals, distance)

            # Black Cell Subobjective
            distance = self.crowding_black_cell(individuals, distance)

            # Bulb Subobjective
            distance = self.crowding_bulb_violations(individuals, distance)

            # normalize data
            out_distances = self.normalize_data(distance, out_distances)

        return out_distances

    def vanilla(self, population):
        """ needed a diversity func for vanilla, just returns population """
        return population

    def calculate_moea_fitness(self, population):
        """ Calculates fitness using MOEA ranking based schema """
        sorted_pop = sorted(population, reverse=True)

        rank = 100
        for count, ind in enumerate(sorted_pop):
            ind.fitness = rank

            if count + 1 == len(sorted_pop):
                break
            if ind > sorted_pop[count + 1]:
                # new level
                rank -= 1

        if self.diversity_algorithm not in self.diversity_vanilla:
            fitness_vals = self.diversity_algs[self.diversity_algorithm](
                sorted_pop)
            sorted_pop = self.update_fitness(population, fitness_vals)
        return sorted_pop

    ###########################################################################
    ################## Survival Selection Algorithms ##########################
    ###########################################################################

    def fitness_proportional_selection_survival(self, individuals):
        """ Selects parents based on fitness probability without replacement.

        individuals - list of Individual objects
        """

        fitness_sum = sum(individuals)
        if fitness_sum == 0:
            return random.choices(individuals, k=self.children * 2)

        probs = [individual.fitness /
                 fitness_sum for individual in individuals]

        return list(np.random.choice(individuals, p=probs, size=self.children * 2, replace=False))

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

    def num_of_evals(self, eval_num, *args, **kwargs):
        """ Stop running if we have reached the max eval number.

        eval_num - current evaluation iteration
        """

        return self.max_evals > eval_num

    def no_change(self, past_n_evals, *args, **kwargs):
        """ Stop running if for the past n runs fitness has not changed

        past_n_evals - past n evals with no change
        """

        return self.n_termination > past_n_evals

        ###########################################################################

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

    def log_generation(self, evals, population):
        """ Logs best individual, and average fitness for current generation.

        evals - current eval count
        population - list of individuals for current generation
        """

        litness = [ind.lit for ind in population]
        avg_lit = round(sum(litness) / len(population), 2)
        best_lit = max(litness)

        black_cell_violations = [
            ind.black_cell_violations for ind in population]
        avg_black_cell_violations = round(sum(
            black_cell_violations) / len(population), 2)
        best_black_cell_violations = min(black_cell_violations)

        bulb_violations = [ind.bulb_violations for ind in population]
        avg_bulb_violations = round(sum(bulb_violations) / len(population), 2)
        best_bulb_violation = min(bulb_violations)

        fit_share = self.fitness_sharing(population)
        avg_fit_share = sum(fit_share.values()) / len(fit_share.values())
        with open(self.log_file, '+a') as file:
            file.write(f"\t{evals}")
            file.write(f"\t{avg_lit}\t{best_lit}")
            file.write(
                f"\t{avg_black_cell_violations}\t{best_black_cell_violations}")
            file.write(f"\t{avg_bulb_violations}\t{best_bulb_violation}")
            file.write(f"\t{avg_fit_share}\n")

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
            file.write(f"\tMax number of evals: {self.max_evals}\n")

            file.write(
                f'\tSurvival algorithm: {self.survival_selection_alg}\n')
            file.write(f'\tParent algorithm: {self.parent_selection_alg}\n')
            file.write(
                f'\tTermination algorithm: {self.termination_alg}\n')
            file.write(
                f'\tSurvival Strategy Algorithm: {self.survival_strategy_alg}\n')
            file.write(f'\tMutation Rate: {self.mutation_rate}\n')
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

    def log_solution(self, best_front, problem_filename):
        """ Log best solution out of all runs.

        fitness_evals - highest fitness achieved out of all runs
        best_solution - best solution out of all runs
        problem_filename - problem file that the solution matches to
        """

        path = '/'.join(self.solution_file.split('/')[:-1])
        Path(path).mkdir(parents=True, exist_ok=True)

        # copies problem file as per specifications of the start for solution files
        copyfile(problem_filename, self.solution_file)
        logging.debug("Logging best solution for all runs at %s\n",
                      self.solution_file)
        with open(self.solution_file, "a") as file:

            for count, individual in enumerate(best_front.individuals):
                file.write(f"Pareto Front Individual #{count}\n\n")
                file.write(
                    f"{individual.lit}\t\
                    {individual.black_cell_violations}\t\
                    {individual.bulb_violations}\n\n")

                file.write("Solution:\n")
                for coordinates in individual.solution:
                    # add one to offset for it starting at 1
                    file.write(
                        f"{coordinates[1]+1} {self.shape[0] - coordinates[0]}\n")

    ###########################################################################
    ######################### Misc Functions  #################################
    ###########################################################################

    @ staticmethod
    def list_extend(list_in, num_to_extend):
        """ Utility function used to arbitrarily extend a list by n length

        list_in - list to extend
        num_to_extend - amount to extend the list by
        """

        list_out = list_in.copy()
        list_out.extend([0] * num_to_extend)
        return list_out

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
        if not isinstance(self.max_evals, int):
            raise MyException(
                "Error: fitness_evals must be an integer in config file")
        if self.survival_strategy_alg in COMMA:
            if self.children < self.parents:
                raise MyException(
                    "Error: λ should be greater than / equal to μ for comma survival strategy runs")
        if self.log_file == self.solution_file:
            raise MyException(
                "Error: Solution file and log file should have different paths")

        # Ensure passed algorithms are supported

        if self.initialization_alg not in self.initialization_algs.keys():
            raise MyException(
                "Error: Provided initialization algorithm not supported")
        if self.parent_selection_alg not in self.parent_algs.keys():
            raise MyException(
                "Error: Provided parent selection algorithm not supported")
        if self.survival_strategy_alg not in SURV_STRAT_ALGS:
            raise MyException(
                "Error: Provided survival strategy algorithm not supported")
        if self.survival_selection_alg not in self.survival_algs.keys():
            raise MyException(
                "Error: Provided survival algorithm not supported")
        if self.termination_alg not in self.termination_algs.keys():
            raise MyException(
                "Error: Provided termination algorithm not supported")
        if self.recombination_alg not in self.recombination_algs.keys():
            raise MyException(
                "Error: Provided recombination algorithm not supported")

    def set_seed(self):
        """Sets random seed value based on object seed variable."""

        if self.seed is None:
            self.seed = int(time.time())
        random.seed(self.seed)
        np.random.seed(self.seed)
