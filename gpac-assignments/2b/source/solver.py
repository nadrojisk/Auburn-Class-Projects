""" Module that implements GP logic to solve PacMan as implemented in gpac.py """
import json
import time
import os
import collections
from pathlib import Path
import random
import glob
import copy
import tqdm
import gpac
import node
import individual
import multiprocessing

Solution = collections.namedtuple('solution', 'fitness contents weights')


class Solver():
    """Solver object for the Pac-Man.

    config_filepath - path to the config file
    """

    ###################################################################
    #######################     Core    ###############################
    ###################################################################

    def __init__(self, config_filepath, show_progress_bar=False, show_board=False):

        # Termination Algorithms
        self.termination_total_eval = {
            'number of evals till termination': self.num_of_evals,
            'num of evals': self.num_of_evals}
        self.termination_no_change = {
            'no change in fitness for n evals': self.no_change,
            'n evals': self.no_change}
        self.termination_algs = {**self.termination_total_eval,
                                 **self.termination_no_change}

        # Parent Selection Algorithms
        self.parent_fps = {'fps': self.fitness_proportional_selection}
        self.parent_over_selection = {'over-selection': self.over_selection}
        self.parent_algs = {**self.parent_fps, **self.parent_over_selection}

        # Survival Selection Algorithms
        self.survival_truncation = {'truncation': self.truncation}
        self.survival_survival_tournament = {'tournament': self.tournament_selection_survival}
        self.survival_algs = {**self.survival_truncation, **self.survival_survival_tournament}

        self.show_progress_bar = show_progress_bar
        self.show_board = show_board
        self.config = config_filepath
        with open(config_filepath) as file:
            config = json.load(file)

            self.pill_density = config.get('pill_density')
            self.fruit_spawn_probability = config.get('fruit_spawn_probability')
            self.fruit_score = config.get('fruit_score')
            self.time_multiplier = config.get('time_multiplier')

            self.seed = config.get('seed')

            self.log_file = config.get('log_file')
            self.solution_file = config.get('solution_file')
            self.highest_score_file = config.get('highest_score_file')

            self.max_runs = config.get('max_runs')
            self.max_evaluations = config.get('max_evaluations')

            self.algorithm = config.get('algorithm')
            self.game_instance = None

            self.top_x_percent = config.get('top_x_percent')
            self.maps = None
            self.run_times = []
            if self.algorithm != 'random':
                # GP
                self.children = config.get('children')  # λ
                self.parents = config.get('parents')  # μ

                # setting K for tournament
                self.tournament_survival = config.get('t_survival')

                # n runs with no change until termination
                self.n_termination = config.get('n')

                self.parsimony_penalty = config.get('parsimony')
                self.parsimony_type = config.get('parsimony_type')
                self.max_depth = config.get('max_depth')

                self.mutation_rate = config.get('mutation_rate')
                try:
                    self.termination_alg = config.get(
                        'termination_alg').lower()
                    self.parent_selection_alg = config.get(
                        'parent_selection_alg').lower()
                    self.survival_selection_alg = config.get(
                        'survival_selection_alg').lower()

                except AttributeError as error:
                    print("Error: Did not provide algorithm")
                    raise AttributeError from error

    def run(self):
        """ Runs solver against a specific map. """
        self._set_seed()
        maps = glob.glob('./maps/map*.txt')
        self.maps = maps
        self._genetic_programming()

    def _genetic_programming(self):

        runs = []

        max_individual_of_experiment = None
        past_evals_with_no_change = 0

        # setup progress bar for runs if correct parameter is passed
        if self.show_progress_bar:
            run_range = tqdm.tqdm(range(self.max_runs), "Run", position=0)
        else:
            run_range = range(self.max_runs)

        for _ in run_range:

            start_time = time.time()
            population = self._create_initial_population()
            eval_counter = len(population)
            max_individual_of_generation = max(population)
            if max_individual_of_experiment is None:
                max_individual_of_experiment = max_individual_of_generation

            max_individual_of_run = max_individual_of_generation

            keep_going = True
            evaluations = collections.OrderedDict()
            evaluations[eval_counter] = population

            # setup progress bar for evaluations if correct parameter is passed
            if self.show_progress_bar:
                eval_range = tqdm.tqdm(range(0, self.max_evaluations, self.children),
                                       "Evaluations", position=1, leave=False)
            else:
                eval_range = range(0, self.max_evaluations, self.children)

            for _ in eval_range:
                if keep_going is False:
                    break

                # parent selection
                parents = self.parent_selection(population)

                # recombination and mutation
                children = self.child_selection(parents)
                eval_counter += len(children)

                population += children

                # survival
                population = self.survival_selection(population)

                # update max individual of generation
                evaluations[eval_counter] = population

                max_population = max(population)
                if max_population > max_individual_of_run:
                    past_evals_with_no_change = 0
                    max_individual_of_run = max_population
                else:
                    past_evals_with_no_change += len(children)

                # check termination criteria
                keep_going = self.termination_selection(eval_counter, past_evals_with_no_change)

            runs.append(evaluations)
            self.run_times.append(time.time() - start_time)

            if max_individual_of_run > max_individual_of_experiment:
                max_individual_of_experiment = max_individual_of_run

        self._log_results(runs)
        self._log_world(max_individual_of_experiment.contents)
        self._log_solution(max_individual_of_experiment.head_node.parse_tree())

    def _create_game(self):
        """ Loads class variable with game instance.

        Game instance should be created per run.
        """
        map_filepath = random.choice(self.maps)
        self.game_instance = gpac.GPac(map_filepath, self.pill_density,
                                       self.fruit_spawn_probability, self.fruit_score,
                                       self.time_multiplier)

    ###########################################################################
    #######################  Algorithm Selection ##############################
    ###########################################################################

    def termination_selection(self, evals, past_n_evals):
        """ Determines whether to end the current run based on termination criteria.
        evals - number of current evals
        past_n_fitnesses - list of past n fitnesses
        max_ind - best individual object of current generation
        """

        terminate = self.termination_algs[self.termination_alg]
        return terminate(eval_num=evals, past_n_evals=past_n_evals)

    def parent_selection(self, population):
        """ Select 2λ - parents for next generation based on chosen algorithm since
        I have chosen to get with a 2 -> 1 reproduction operator(2 parents, 1 child)

        population - list of individuals to be used to create the next generation
        """
        population = self.parent_algs[self.parent_selection_alg](population)
        return population

    def child_selection(self, population):
        """ Generate child using recombination and mutation.

        population - list of individuals that make up the parents for the children
        maps - list of maps that can be selected for the games
        """

        children = []
        for _ in range(self.children):
            parent_one, parent_two = random.sample(population, 2)
            parent_one = parent_one.head_node
            parent_two = parent_two.head_node
            rng = random.random()
            if rng < self.mutation_rate:
                # mutate
                if random.randint(0, 1):
                    parent = parent_one
                else:
                    parent = parent_two
                child_node = self.sub_tree_mutation(parent)
            else:
                child_node = self.sub_tree_crossover(parent_one, parent_two)
            children.append(child_node)

        return self.create_individuals(children)

    def survival_selection(self, population):
        """ Selects μ - individuals to survive into the next generation based on
        a chosen algorithm.

        population - list of old individuals from prior generation
        """

        population = self.survival_algs[self.survival_selection_alg](
            population)
        return population

    ###########################################################################
    ################### Parent Selection Algorithms ###########################
    ###########################################################################

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

    def over_selection(self, individuals):
        """ Splits populations into two groups, the top x% and the other (100-x)%
        After that 80% of the selected individuals will come from the top x% and
        the remained 20% will come from the other group.
        """

        sorted_population = sorted(individuals, reverse=True)
        num_of_individuals = len(sorted_population)
        top_n = self.top_x_percent * num_of_individuals

        top_population = sorted_population[top_n:]
        bottom_population = sorted_population[:top_n]

        top = random.choices(top_population, k=.8 * num_of_individuals)
        bottom = random.choices(bottom_population, k=.2 * num_of_individuals)

        return top + bottom

    ###########################################################################
    ###################### Survival Algorithms #############################
    ###########################################################################

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

        return self.max_evaluations > eval_num

    def no_change(self, past_n_evals, *args, **kwargs):
        """ Stop running if for the past n runs fitness has not changed
        past_n_evals - past n evals with no change
        """

        return self.n_termination > past_n_evals

    ###########################################################################
    ######################## Genetic Programming ##############################
    ###########################################################################

    def _create_initial_population(self):
        """ Creates initial random solution. """
        population = []
        if self.show_progress_bar:

            run_range = tqdm.tqdm(range(self.parents), "Initial Population",
                                  position=1, leave=False, total=self.parents)
        else:
            run_range = range(self.parents)

        for _ in run_range:
            # create tree
            if random.randint(0, 1):
                tree_type = 'full'
            else:
                tree_type = 'grow'
            head = node.Node(tree_type=tree_type, max_depth=self.max_depth)
            head.grow()
            population.append(head)

        # play game and return individual

        return self.create_individuals(population)

    def create_individuals(self, population):
        out = []
        with multiprocessing.Pool() as pool:
            for i, res in enumerate(pool.imap_unordered(self.calculate_fitness, population)):
                out.append(res)
        return out

    def calculate_fitness(self, head):
        """ Creates a game instance with a random map picked from the maps variable.
        Game is played until completion and it's score and game contents are recorded.
        """
        current_score = 0
        contents = ''

        self._create_game()
        while not self.game_instance.is_gameover:
            current_score, contents = self._turn(head)

        if self.parsimony_type == "total":
            count = head.get_total_nodes()
        else:
            count = head.get_height()
        penalty = self.parsimony_penalty * count
        final_score = current_score - penalty
        current_solution = individual.Individual(final_score, current_score, contents, head)
        return current_solution

    ###################################################################
    #############     Recombination / Mutation    #####################
    ###################################################################

    @staticmethod
    def sub_tree_crossover(parent_one_original, parent_two_original):
        """ Crosses two tree's at two random nodes """

        parent_one = copy.deepcopy(parent_one_original)

        # find node one
        parent_one_list = parent_one.to_list()
        child_one = random.choice(random.choice(parent_one_list))

        parent_two = copy.deepcopy(parent_two_original)

        # find node two
        parent_two_list = parent_two.to_list()

        child_two = random.choice(random.choice(parent_two_list))

        # swap node over
        child_one.swap(child_two)

        return parent_one

    @staticmethod
    def sub_tree_mutation(head):
        """ Selects a random node in the passed tree structure.
        This node is reset and a tree is grown from it.
        """

        head = copy.deepcopy(head)
        mutated_node = random.choice(random.choice(head.to_list()))
        mutated_node.children = [None, None]
        mutated_node.data = mutated_node.generate_value()
        mutated_node.grow()

        return head

    ###################################################################
    ###############     Distance Calculation    #######################
    ###################################################################

    def _closest_ghost(self, cell):
        """ Calculate manhattan distance for closest ghost to Pac-Man. """
        distances = []

        for ghost in gpac.GHOST:
            ghost_loc = self.game_instance.locations[ghost]

            distances.append(self._calculate_manhattan_distance(cell, ghost_loc))

        return min(distances)

    def _closest_pill(self, cell):
        """ Calculate manhattan distance for closest pill to Pac-Man. """
        min_distance = 0
        seen = [cell]
        possible_locations = [cell]
        found = False
        while not found:
            current = possible_locations.pop()

            if self.game_instance.board[current[0]][current[1]] == gpac.PILL:
                found = True
                min_distance = self._calculate_manhattan_distance(cell, current)
                break

            locations = self.game_instance.get_all_spots_around_cell(current)
            for location in locations:
                if location not in seen:
                    seen.append(location)
                    possible_locations.append(location)

        return min_distance

    def _closest_fruit(self, cell):
        """ Calculate manhattan distance for closest fruit to pacman.

        Note: there is only one fruit at a time, therefore the only fruit is the
        closest fruit.
        """

        fruit_loc = self.game_instance.locations[gpac.FRUIT]
        if fruit_loc:
            return self._calculate_manhattan_distance(cell, fruit_loc)
        return 0

    def _calculate_adjacent_walls(self, cell):
        """ Calculate walls adjacent to Pac-Man. """
        locs = self.game_instance.get_all_spots_around_cell(cell)
        num_of_walls = 0

        for loc in locs:
            if self.game_instance.board[loc[0]][loc[1]] == '#':
                num_of_walls += 1

        return num_of_walls

    ###################################################################
    ##################     Sensor Inputs    ###########################
    ###################################################################

    @staticmethod
    def _generate_pacman_weights():
        """ Calculates weight vector for Pac-Man """
        weights = []
        for _ in range(4):
            rng = random.uniform(-1, 1)
            weights.append(rng)
        return weights

    def _generate_sensor_inputs(self, cell):
        """ Generates sensor inputs for a given location.

        cell - location to calculate inputs on
        """

        manhattan_ghost = self._closest_ghost(cell)
        manhattan_pill = self._closest_pill(cell)
        number_of_walls = self._calculate_adjacent_walls(cell)
        manhattan_fruit = self._closest_fruit(cell)

        return [manhattan_ghost, manhattan_pill, number_of_walls, manhattan_fruit]

    ###################################################################
    ######################     Turn    #############################
    ###################################################################

    def _turn(self, root_node):
        """ Run a single turn through the pac-man game. """

        # calculates best move for pac-man
        move_scores = self._calculate_move_scores(root_node)

        pacman_move = self._select_best_move(move_scores)

        # move pacman
        self.game_instance.move(pacman_move, gpac.PACMAN)

        # move ghosts
        for ghost in gpac.GHOST:
            ghosts_moves = random.choice(self.game_instance.get_moves_for_unit(ghost))
            self.game_instance.move(ghosts_moves, ghost)
        return self.game_instance.turn()

    @staticmethod
    def _select_best_move(move_scores):
        """ Selects best move out of selection of different scores each correlating to a move
        direction.

        move_scores - dictionary with keys of move direction and values of scores
        relating to the move
        """

        max_score = max(move_scores.values())
        pacman_move = None
        for move_direction in move_scores.keys():
            if move_scores[move_direction] == max_score:
                pacman_move = move_direction
                break
        return pacman_move

    def _calculate_move_scores(self, root_node):
        """ Calculates scores for every move Pac-Man can make based on weighted vector. """
        move_choices = {}
        for move in self.game_instance.get_spots_around_unit(gpac.PACMAN):
            sensor_values = self._generate_sensor_inputs(move)

            move_score = root_node.calculate(*sensor_values)

            pacman_loc = self.game_instance.locations[gpac.PACMAN]
            move_direction = self.game_instance.location_to_cardinal(pacman_loc, move)

            move_choices[move_direction] = move_score
        return move_choices

    ###################################################################
    ######################     Logging    #############################
    ###################################################################

    def _log_solution(self, tree):
        """ Log best solution of all time's expressions. """

        self._create_path(self.solution_file)
        with open(self.solution_file, "+w") as file:
            file.write(tree)
            file.write("\n")

    def _log_world(self, contents):
        """ Log best solution of a time's world contents. """

        self._create_path(self.highest_score_file)
        with open(self.highest_score_file, "+w") as file:
            file.write(contents)

    def _log_parameters(self):
        total_time = sum(self.run_times)
        outputs = 'Configuration Information\n\n'
        outputs += f'\tSolution File Path: {self.solution_file}\n'
        outputs += f'\tSeed: {self.seed}\n'
        outputs += f'\tNumber of runs: {self.max_runs}\n'
        outputs += f'\tNumber of evaluation: {self.max_evaluations}\n'
        outputs += f'\tPill density: {self.pill_density}\n'
        outputs += f'\tFruit spawn chance: {self.fruit_spawn_probability}\n'
        outputs += f'\tFruit score: {self.fruit_score}\n'
        outputs += f'\tTime multiplier: {self.time_multiplier}\n\n'
        outputs += f'\tAverage Run Time: {total_time/self.max_runs}\n'
        outputs += f'\tTotal Experiment Time: {total_time}\n\n'
        return outputs

    def _log_results(self, runs):
        """ Log runs to result file.

        Evaluations should be logged as the highest solution of a run is beaten.
        """

        self._create_path(self.log_file)
        with open(self.log_file, "+w") as file:
            file.write("Result Log\n\n")

            file.write(self._log_parameters())
            for count, run_info in enumerate(runs):
                file.write(f"Run {count+1}\n")

                for evals, population in run_info.items():
                    best_individual = sorted(population, key=lambda x: x.score, reverse=True)[0]

                    pop_sum = sum([pop.score for pop in population])
                    avg_fitness = round(pop_sum / len(population), 2)
                    file.write(f"\t{evals}\t{avg_fitness}\t{best_individual.score}\n")
                file.write("\n")

    ###################################################################
    ####################     Utilities    #############################
    ###################################################################

    def _set_seed(self):
        """Sets random seed value based on object seed variable."""

        if self.seed is None:
            self.seed = int(time.time())
        random.seed(self.seed)
        # np.random.seed(self.seed)

    @ staticmethod
    def _calculate_manhattan_distance(point_a, point_b):
        """ Calculate manhattan distance for two points. """
        distance = (point_a[0] + point_a[1]) - (point_b[0] + point_b[1])
        if distance < 0:
            distance = -distance
        return distance

    @ staticmethod
    def _create_path(filepath):
        """ Recursively creates path. """
        path = os.path.split(filepath)[0]
        Path(path).mkdir(parents=True, exist_ok=True)
