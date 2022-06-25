""" Module that implements GP logic to solve PacMan as implemented in gpac.py """
import json
import time
import os
import collections
from pathlib import Path
import random
import glob
import copy
import multiprocessing
from functools import lru_cache
import numpy
from PIL import Image
import tqdm
import gpac
import node
import shortest_path
import individual


class Solver():
    """Solver object for the Pac-Man.

    config_filepath - path to the config file
    """

    ###################################################################
    #######################     Core    ###############################
    ###################################################################

    def __init__(self, config_filepath, show_progress_bar=False, show_board=False):

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
            self.ghost_solution_file = config.get('ghost_solution_file')
            self.pacman_solution_file = config.get('pacman_solution_file')
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
                self.ghost_children = config.get('ghost_children')  # ghost_λ
                self.ghost_parents = config.get('ghost_parents')  # ghost_μ
                self.pacman_children = config.get('pacman_children')  # pacman_λ
                self.pacman_parents = config.get('pacman_parents')  # pacman_μ

                # setting K for tournament
                self.pacman_tournament_survival = config.get('pacman_t_survival')
                self.ghost_tournament_survival = config.get('ghost_t_survival')

                # n runs with no change until termination
                self.n_termination = config.get('n')

                self.ghost_parsimony_penalty = config.get('ghost_parsimony')
                self.pacman_parsimony_penalty = config.get('pacman_parsimony')

                self.max_depth = config.get('max_depth')

                self.ghost_mutation_rate = config.get('ghost_mutation_rate')
                self.pacman_mutation_rate = config.get('pacman_mutation_rate')
                self.ciao_file = config.get('ciao_file')
                try:
                    self.ghost_parent_selection_alg = config.get(
                        'ghost_parent_selection_alg').lower()
                    self.pacman_parent_selection_alg = config.get(
                        'pacman_parent_selection_alg').lower()
                    self.ghost_survival_selection_alg = config.get(
                        'ghost_survival_selection_alg').lower()
                    self.pacman_survival_selection_alg = config.get(
                        'pacman_survival_selection_alg').lower()

                except AttributeError as error:
                    print("Error: Did not provide algorithm")
                    raise AttributeError from error

    def run(self):
        """ Runs solver against a specific map. """
        self._set_seed()
        maps = glob.glob('./maps/map*.txt')
        self.maps = maps
        self._genetic_programming()

    def reevaluate(self, pacman_population, ghost_population, pacman_children, ghost_children):
        """ Used for reevaluating individuals. Expects the current pacman and ghost population
        and both pacman and ghost children.
        """

        pacman_nodes = [pacman.head_node for pacman in pacman_population]
        ghost_nodes = [ghost.head_node for ghost in ghost_population]

        pacman_nodes += pacman_children
        ghost_nodes += ghost_children

        return self.create_individuals(pacman_nodes, ghost_nodes)

    def _genetic_programming(self):

        runs = []
        best_pacmans_overall = []
        best_ghosts_overall = []
        # setup progress bar for runs if correct parameter is passed
        if self.show_progress_bar:
            run_range = tqdm.tqdm(range(self.max_runs), "Run", position=0)
        else:
            run_range = range(self.max_runs)

        for run in run_range:

            best_pacmans = []
            best_ghosts = []
            start_time = time.time()

            # create initial population for run and increase eval_counter
            pacman_population, ghost_population = self._create_initial_populations()
            eval_counter = len(pacman_population)

            # find the best pacman and ghost
            best_pacmans.append(max(pacman_population))
            best_ghosts.append(max(ghost_population))

            keep_going = True
            evaluations = collections.OrderedDict()
            evaluations[eval_counter] = pacman_population

            # setup progress bar for evaluations if correct parameter is passed
            if self.show_progress_bar:
                eval_range = tqdm.tqdm(range(0, self.max_evaluations - len(pacman_population),
                                             self.pacman_children + self.pacman_parents),
                                       "Evaluations", position=1, leave=False)
            else:
                eval_range = range(0, self.max_evaluations - len(pacman_population),
                                   self.pacman_children + self.pacman_parents)

            for _ in eval_range:
                if keep_going is False:
                    break

                # parent selection
                pacman_parents = self.parent_selection(pacman_population, gpac.PACMAN)
                ghost_parents = self.parent_selection(ghost_population, gpac.GHOST)

                # recombination and mutation
                pacman_children = self.child_selection(pacman_parents, gpac.PACMAN)
                ghost_children = self.child_selection(ghost_parents, gpac.GHOST)

                # revaluate
                pacman_population, ghost_population = self.reevaluate(
                    pacman_population, ghost_population, pacman_children, ghost_children)

                eval_counter += len(pacman_population)

                # survival
                pacman_population = self.survival_selection(pacman_population, gpac.PACMAN)
                ghost_population = self.survival_selection(ghost_population, gpac.GHOST)

                # update max individual of generation
                evaluations[eval_counter] = pacman_population

                best_pacmans.append(max(pacman_population))
                best_ghosts.append(max(ghost_population))

                # check termination criteria
                keep_going = self.termination_selection(eval_counter)

            runs.append(evaluations)
            self.run_times.append(time.time() - start_time)

            self.gen_ciao_plot(best_pacmans, best_ghosts, run)

            best_pacmans_overall.append(max(best_pacmans))
            best_ghosts_overall.append(max(best_ghosts))

        best_pacman = max(best_pacmans_overall)
        best_ghost = max(best_ghosts_overall)
        pacman, _ = self.create_individuals([best_pacman.head_node], [best_ghost.head_node])
        self._log_results(runs)
        self._log_world(pacman[0].contents, best_ghost.contents)
        self._log_solution(best_pacman.head_node.parse_tree(),
                           best_ghost.head_node.parse_tree())

    def gen_ciao_plot(self, pacmans, ghosts, run):
        """ Create CIAO plot for experiment. """

        fitnesses = []

        for gen, pacman in enumerate(pacmans):
            fitnesses.append([])

            ghost_heads = [ghost.head_node for ghost in ghosts[:gen + 1]]
            pacman_heads = [pacman.head_node for _ in range(gen + 1)]
            population = list(zip(pacman_heads, ghost_heads))
            with multiprocessing.Pool() as pool:
                for _, res in enumerate(pool.imap_unordered(self.calculate_fitness, population)):

                    fitnesses[-1].append(res[0].fitness)

        data = numpy.full((len(pacmans), len(pacmans), 3), 255, dtype=numpy.uint8)

        for row, fitness in enumerate(fitnesses):
            fitness = Solver.normalize_fitnesses(fitness)
            for col, fit in enumerate(fitness):
                luminance = (1 - fit) * 255
                data[-(row + 1)][col] = [luminance, luminance, luminance]
        img = Image.fromarray(data)
        path, ext = os.path.splitext(self.ciao_file)
        path += str(run) + ext
        self._create_path(path)
        img.save(path)

    @ staticmethod
    def normalize_fitnesses(fitnesses):
        min_fitness = min(fitnesses)

        constant = min_fitness * -1

        mod_fitnesses = [fitness + constant for fitness in fitnesses]
        max_mod_fitness = max(mod_fitnesses)
        if max_mod_fitness:
            return [fitness / max_mod_fitness for fitness in mod_fitnesses]
        else:
            return mod_fitnesses

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

    def termination_selection(self, evals):
        """ Determines whether to end the current run based on termination criteria.
        evals - number of current evals
        past_n_fitnesses - list of past n fitnesses
        max_ind - best individual object of current generation
        """
        return self.num_of_evals(eval_num=evals)

    def parent_selection(self, population, unit):
        """ Select 2λ - parents for next generation based on chosen algorithm since
        I have chosen to get with a 2 -> 1 reproduction operator(2 parents, 1 child)

        population - list of individuals to be used to create the next generation
        """
        if unit == gpac.PACMAN:
            parent_selection_alg = self.pacman_parent_selection_alg
        else:
            parent_selection_alg = self.ghost_parent_selection_alg

        population = self.parent_algs[parent_selection_alg](population, unit)
        return population

    def child_selection(self, population, unit):
        """ Generate child using recombination and mutation.

        population - list of individuals that make up the parents for the children
        maps - list of maps that can be selected for the games
        """
        if unit == gpac.PACMAN:
            num_of_children = self.pacman_children
            mutation_rate = self.pacman_mutation_rate
        else:
            num_of_children = self.ghost_children
            mutation_rate = self.ghost_mutation_rate

        children = []
        for _ in range(num_of_children):
            parent_one, parent_two = random.sample(population, 2)
            parent_one = parent_one.head_node
            parent_two = parent_two.head_node
            rng = random.random()
            if rng < mutation_rate:
                # mutate
                if random.randint(0, 1):
                    parent = parent_one
                else:
                    parent = parent_two
                child_node = self.sub_tree_mutation(parent)
            else:
                child_node = self.sub_tree_crossover(parent_one, parent_two)
            children.append(child_node)

        return children

    def survival_selection(self, population, unit):
        """ Selects μ - individuals to survive into the next generation based on
        a chosen algorithm.

        population - list of old individuals from prior generation
        """
        if unit == gpac.PACMAN:
            survival_selection_alg = self.pacman_survival_selection_alg
        else:
            survival_selection_alg = self.ghost_survival_selection_alg

        population = self.survival_algs[survival_selection_alg](
            population, unit)
        return population

    ###########################################################################
    ################### Parent Selection Algorithms ###########################
    ###########################################################################

    def fitness_proportional_selection(self, individuals, unit):
        """ Selects parents based on fitness probability.

        individuals - list of Individual objects
        """
        children = self.pacman_children if unit == gpac.PACMAN else self.ghost_children
        fitness_sum = sum(individuals)
        if fitness_sum == 0:
            return random.choices(individuals, k=children * 2)

        probs = [individual.fitness /
                 fitness_sum for individual in individuals]

        return random.choices(individuals, probs, k=children * 2)

    def over_selection(self, individuals):
        """ Splits populations into two groups, the top x% and the other (100-x)%
        After that 80% of the selected individuals will come from the top x% and
        the remained 20% will come from the other group.
        """

        sorted_population = sorted(individuals, reverse=True)
        num_of_individuals = len(sorted_population)
        top_n = self.top_x_percent * num_of_individuals

        top_population = sorted_population[top_n:]
        bottom_population = sorted_population[: top_n]

        top = random.choices(top_population, k=.8 * num_of_individuals)
        bottom = random.choices(bottom_population, k=.2 * num_of_individuals)

        return top + bottom

    ###########################################################################
    ###################### Survival Algorithms #############################
    ###########################################################################

    def truncation(self, individuals, unit):
        """ Selects μ best individuals

        individuals: list of Individual objects
        """
        parents = self.pacman_parents if unit == gpac.PACMAN else self.ghost_parents
        return sorted(individuals, reverse=True)[: parents]

    def tournament_selection_survival(self, individuals, unit):
        """ Selects parents using a tournament based system. Grabs k individuals
        and selects the best individual out of that set.

        For survival selection we will not be using replacement

        individuals: list of Individual objects
        """
        parents = self.pacman_parents if unit == gpac.PACMAN else self.ghost_parents
        k_tourn = self.pacman_tournament_survival if unit == gpac.PACMAN \
            else self.pacman_tournament_survival
        chosen = []
        for _ in range(parents):

            selection = random.sample(individuals, k=k_tourn)

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

        return self.max_evaluations > eval_num

    ###########################################################################
    ######################## Genetic Programming ##############################
    ###########################################################################

    def _create_initial_population(self, unit):
        """ Creates initial random solution. """
        population = []
        for _ in range(self.pacman_parents):
            # create tree
            if random.randint(0, 1):
                tree_type = 'full'
            else:
                tree_type = 'grow'
            head = node.Node(tree_type=tree_type, depth_limit=self.max_depth, unit=unit)
            head.grow()
            population.append(head)
        return population

    def _create_initial_populations(self):

        pops = []

        pops.append(self._create_initial_population(gpac.PACMAN))
        pops.append(self._create_initial_population(gpac.GHOST))
        # play game and return individual
        return self.create_individuals(pops[0], pops[1])

    def create_individuals(self, pacman_population, ghost_population):
        pacman_ind = []
        ghost_ind = []
        population = list(zip(pacman_population, ghost_population))
        with multiprocessing.Pool() as pool:
            for _, res in enumerate(pool.imap_unordered(self.calculate_fitness, population)):
                pacman_ind.append(res[0])
                ghost_ind.append(res[1])
        return pacman_ind, ghost_ind

    def calculate_fitness(self, controllers):
        """ Creates a game instance with a random map picked from the maps variable.
        Game is played until completion and it's score and game contents are recorded.
        """
        current_score = 0
        contents = ''
        pacman, ghost = controllers
        self._create_game()
        pacman_eaten = False
        while not self.game_instance.is_gameover:
            current_score, contents, pacman_eaten = self._turn(pacman, ghost)

        pacman_count = pacman.get_total_nodes()
        ghost_count = ghost.get_total_nodes()

        pacman_penalty = self.pacman_parsimony_penalty * pacman_count
        ghost_penalty = self.ghost_parsimony_penalty * ghost_count

        pacman_score = current_score - pacman_penalty

        ghost_bonus = 100 if pacman_eaten else 0
        ghost_score = 1 / (1 if (current_score - ghost_penalty +
                                 1) == 0 else (current_score - ghost_penalty + 1)) + ghost_bonus
        pacman_solution = individual.Individual(pacman_score, current_score, contents, pacman)
        ghost_solution = individual.Individual(ghost_score, current_score, contents, ghost)
        return [pacman_solution, ghost_solution]

    ###################################################################
    #############     Recombination / Mutation    #####################
    ###################################################################

    @ staticmethod
    def sub_tree_crossover(parent_one_original, parent_two_original):
        """ Crosses two tree's at two random nodes """

        not_found = True
        parent_one = copy.deepcopy(parent_one_original)

        # find node one
        parent_one_list = parent_one.to_list()
        child_one = random.choice(random.choice(parent_one_list))

        parent_two = copy.deepcopy(parent_two_original)
        parent_two_list = parent_two.to_list()

        while not_found:
            # find node two

            child_two = random.choice(random.choice(parent_two_list))

            if (child_one.depth + child_two.get_height()) <= parent_one.max_depth:
                not_found = False
            else:
                continue

            # swap node over
            child_one.swap(child_two)

        return parent_one

    @ staticmethod
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

            distances.append(self._calculate_manhattan_distance(tuple(cell), tuple(ghost_loc)))

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
                min_distance = self._calculate_manhattan_distance(tuple(cell), tuple(current))
                break

            locations = self.game_instance.get_all_spots_around_cell(current)
            for location in locations:
                if location not in seen:
                    seen.append(location)
                    possible_locations.append(location)

        return min_distance

    def _shortest_pacman_distance(self, cell):
        pacman_loc = self.game_instance.locations[gpac.PACMAN]
        board = tuple([tuple(row) for row in self.game_instance.board])
        return shortest_path.BFS(board, tuple(cell), tuple(pacman_loc))

    def _shortest_ghost_distance(self, cell):
        """ Calculate shortest path distance for closest ghost to Pac-Man. """
        distances = []
        board = tuple([tuple(row) for row in self.game_instance.board])

        for ghost in gpac.GHOST:
            ghost_loc = self.game_instance.locations[ghost]

            distances.append(shortest_path.BFS(board, tuple(cell), tuple(ghost_loc)))

        return min(distances)

    def _closest_fruit(self, cell):
        """ Calculate manhattan distance for closest fruit to pacman.

        Note: there is only one fruit at a time, therefore the only fruit is the
        closest fruit.
        """

        fruit_loc = self.game_instance.locations[gpac.FRUIT]
        if fruit_loc:
            return self._calculate_manhattan_distance(tuple(cell), tuple(fruit_loc))
        return 0

    def _pacman_distance(self, cell):
        pacman_loc = self.game_instance.locations[gpac.PACMAN]
        return self._calculate_manhattan_distance(tuple(cell), tuple(pacman_loc))

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

    @ staticmethod
    def _generate_pacman_weights():
        """ Calculates weight vector for Pac-Man """
        weights = []
        for _ in range(4):
            rng = random.uniform(-1, 1)
            weights.append(rng)
        return weights

    def _generate_sensor_inputs(self, cell, unit):
        """ Generates sensor inputs for a given location.

        cell - location to calculate inputs on
        """
        if unit == gpac.PACMAN:
            manhattan_ghost = self._closest_ghost(cell)
            manhattan_pill = self._closest_pill(cell)
            number_of_walls = self._calculate_adjacent_walls(cell)
            manhattan_fruit = self._closest_fruit(cell)
            ghost_shortest = self._shortest_ghost_distance(cell)
            return [
                manhattan_ghost, manhattan_pill, number_of_walls, manhattan_fruit, ghost_shortest]
        else:
            manhattan_ghost = self._closest_ghost(cell)
            manhattan_pacman = self._pacman_distance(cell)
            shortest_pacman = self._shortest_pacman_distance(cell)
            return [manhattan_ghost, manhattan_pacman, shortest_pacman]

    ###################################################################
    ######################     Turn    #############################
    ###################################################################

    def _turn(self, pacman_controller, ghost_controller):
        """ Run a single turn through the pac-man game. """

        # calculates best move for pac-man
        move_scores = self._calculate_move_scores(pacman_controller, gpac.PACMAN)
        pacman_move = self._select_best_move(move_scores, gpac.PACMAN)

        # move ghosts
        ghosts_moves = []
        for ghost in gpac.GHOST:
            move_scores = self._calculate_move_scores(ghost_controller, ghost)
            ghost_move = self._select_best_move(move_scores, gpac.GHOST)
            ghosts_moves.append(ghost_move)

        # move pacman
        self.game_instance.move(pacman_move, gpac.PACMAN)

        # move ghosts
        for move, ghost in zip(ghosts_moves, gpac.GHOST):
            self.game_instance.move(move, ghost)

        return self.game_instance.turn()

    @ staticmethod
    def _select_best_move(move_scores, unit):
        """ Selects best move out of selection of different scores each correlating to a move
        direction.

        move_scores - dictionary with keys of move direction and values of scores
        relating to the move
        """
        compare = max if unit == gpac.PACMAN else min
        max_score = compare(move_scores.values())
        move = None
        for move_direction in move_scores.keys():
            if move_scores[move_direction] == max_score:
                move = move_direction
                break
        return move

    def _calculate_move_scores(self, root_node, unit):
        """ Calculates scores for every move Pac-Man can make based on weighted vector. """
        move_choices = {}
        for move in self.game_instance.get_spots_around_unit(unit):
            sensor_values = self._generate_sensor_inputs(move, unit)

            move_score = root_node.calculate(*sensor_values)

            location = self.game_instance.locations[unit]
            move_direction = self.game_instance.location_to_cardinal(location, move)

            move_choices[move_direction] = move_score
        return move_choices

    ###################################################################
    ######################     Logging    #############################
    ###################################################################

    def _log_solution(self, pacman_tree, ghost_tree):
        """ Log best solution of all time's expressions. """

        self._create_path(self.pacman_solution_file)
        with open(self.pacman_solution_file, "+w") as file:
            file.write(pacman_tree)
            file.write("\n")

        self._create_path(self.pacman_solution_file)
        with open(self.ghost_solution_file, "+w") as file:
            file.write(ghost_tree)
            file.write("\n")

    def _log_world(self, pacman_contents, ghost_contents):
        """ Log best solution of a time's world contents. """

        self._create_path(self.highest_score_file)
        with open(self.highest_score_file, "+w") as file:
            file.write(pacman_contents)

    def _log_parameters(self):
        total_time = sum(self.run_times)
        outputs = 'Configuration Information\n\n'
        outputs += f'\tPacman Solution File Path: {self.pacman_solution_file}\n'
        outputs += f'\tGhost Solution File Path: {self.ghost_solution_file}\n'
        outputs += f'\tSeed: {self.seed}\n'
        outputs += f'\tPacman Children: {self.pacman_children}\n'
        outputs += f'\tPacman Parents: {self.pacman_parents}\n'
        outputs += f'\tGhost Children: {self.ghost_children}\n'
        outputs += f'\tGhost Parents: {self.ghost_parents}\n'
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

    @ lru_cache(maxsize=1000)
    def _calculate_manhattan_distance(self, point_a, point_b):
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
