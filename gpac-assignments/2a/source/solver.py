""" Module that implements GP logic to solve PacMan as implemented in gpac.py """
import json
import time
import os
import collections
from pathlib import Path
import random
import gpac
import tqdm


Solution = collections.namedtuple('solution', 'fitness contents weights')


class Solver():
    """Solver object for the Pac-Man.

    config_filepath - path to the config file
    """

    ###################################################################
    #######################     Core    ###############################
    ###################################################################

    def __init__(self, config_filepath, show_progress_bar=False, show_board=False):
        self.base_algorithm = {'random': self._random_search}
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

    def run(self, map_filepath):
        """ Runs solver against a specific map. """
        self._set_seed()
        self.base_algorithm[self.algorithm](map_filepath)

    def _random_search(self, map_filepath):
        """Random Search solver algorithm. Randomly picks 3 moves for the ghosts
        and determines the best move for Pac-Man based on a weighted sensor input vector.

        map_filepath - path to map to create
        """

        runs = []

        highest_solution_overall = Solution(0, '', [])

        if self.show_progress_bar:
            run_range = tqdm.tqdm(range(self.max_runs), "Run", position=0)
        else:
            run_range = range(self.max_runs)

        for _ in run_range:

            # play game
            highest_solution_in_run = Solution(0, '', [])
            highest_solution_overall = Solution(0, '', [])
            current_solution = Solution(0, '', [])

            evaluations = collections.OrderedDict()
            if self.show_progress_bar:
                eval_range = tqdm.tqdm(range(self.max_evaluations),
                                       "Evaluation", position=1, leave=False)
            else:
                eval_range = range(self.max_evaluations)

            for evaluation in eval_range:
                self._create_game(map_filepath)
                pac_weights = self._generate_pacman_weights()
                while not self.game_instance.is_gameover:
                    if self.show_board:
                        self.game_instance.print_board()
                        time.sleep(0.10)
                    current_score, contents = self._turn(pac_weights)
                    current_solution = Solution(current_score, contents, pac_weights)

                if current_solution.fitness > highest_solution_in_run.fitness:
                    highest_solution_in_run = current_solution
                    evaluations[evaluation] = current_solution

            runs.append(evaluations)

            if highest_solution_in_run.fitness > highest_solution_overall.fitness:
                highest_solution_overall = highest_solution_in_run

        self._log_results(runs, map_filepath)
        self._log_world(highest_solution_overall.contents)
        self._log_solution(highest_solution_overall.weights)

    def _create_game(self, world_filepath):
        """ Loads class variable with game instance.

        Game instance should be created per run.
        """

        self.game_instance = gpac.GPac(world_filepath, self.pill_density,
                                       self.fruit_spawn_probability, self.fruit_score,
                                       self.time_multiplier)

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
        pill_locations = self.game_instance.locations[gpac.PILL]

        min_distance = self._calculate_manhattan_distance(cell, pill_locations[0])

        for pill_loc in pill_locations[1:]:
            current_distance = self._calculate_manhattan_distance(cell, pill_loc)
            if min_distance > current_distance:
                min_distance = current_distance

        return min_distance

    def _closest_fruit(self, cell):
        """ Calculate manhattan distance for closest fruit to pacman.

        Note: there is only one fruit at a time, therefore the only fruit is the
        closest fruit.
        """

        fruit_loc = self.game_instance.locations[gpac.FRUIT]
        if fruit_loc:
            return self._calculate_manhattan_distance(cell, fruit_loc)
        return 500

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

    def _turn(self, pac_weights):
        """ Run a single turn through the pac-man game. """

        # calculates best move for pac-man
        move_scores = self._calculate_move_scores(pac_weights)

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

    def _calculate_move_scores(self, pac_weights):
        """ Calculates scores for every move Pac-Man can make based on weighted vector. """

        move_choices = {}
        for move in self.game_instance.get_spots_around_unit(gpac.PACMAN):
            sensor_values = self._generate_sensor_inputs(move)

            move_score = sum([sensor * weight for sensor,
                              weight in zip(sensor_values, pac_weights)])

            pacman_loc = self.game_instance.locations[gpac.PACMAN]
            move_direction = self.game_instance.location_to_cardinal(pacman_loc, move)

            move_choices[move_direction] = move_score
        return move_choices

    ###################################################################
    ######################     Logging    #############################
    ###################################################################

    def _log_solution(self, weights):
        """ Log best solution of all time's expressions. """

        self._create_path(self.solution_file)
        sensors = ['G', 'P', 'W', 'F']
        with open(self.solution_file, "+w") as file:
            for count, contents in enumerate(zip(sensors, weights)):
                sensor, weight = contents
                if count:
                    file.write(" + ")
                file.write(f"{weight}*{sensor}")
            file.write("\n")

    def _log_world(self, contents):
        """ Log best solution of a time's world contents. """

        self._create_path(self.highest_score_file)
        with open(self.highest_score_file, "+w") as file:
            file.write(contents)

    def _log_parameters(self, problem_path):
        outputs = 'Configuration Information\n\n'
        outputs += f'\tProblem Instance File Path: {problem_path}\n'
        outputs += f'\tSolution File Path: {self.solution_file}\n'
        outputs += f'\tSeed: {self.seed}\n'
        outputs += f'\tNumber of runs: {self.max_runs}\n'
        outputs += f'\tNumber of evaluation: {self.max_evaluations}\n'
        outputs += f'\tPill density: {self.pill_density}\n'
        outputs += f'\tFruit spawn chance: {self.fruit_spawn_probability}\n'
        outputs += f'\tFruit score: {self.fruit_score}\n'
        outputs += f'\tTime multiplier: {self.time_multiplier}\n\n'
        return outputs

    def _log_results(self, runs, map_filepath):
        """ Log runs to result file.

        Evaluations should be logged as the highest solution of a run is beaten.
        """

        self._create_path(self.log_file)
        with open(self.log_file, "+w") as file:
            file.write("Result Log\n\n")

            file.write(self._log_parameters(map_filepath))
            for count, run_info in enumerate(runs):
                file.write(f"Run {count+1}\n")

                for evaluation, eval_info in run_info.items():
                    score = eval_info.fitness
                    file.write(f"{evaluation}\t{score}\n")
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

    @staticmethod
    def _calculate_manhattan_distance(point_a, point_b):
        """ Calculate manhattan distance for two points. """
        distance = (point_a[0] + point_a[1]) - (point_b[0] + point_b[1])
        if distance < 0:
            distance = -distance
        return distance

    @staticmethod
    def _create_path(filepath):
        """ Recursively creates path. """
        path = os.path.split(filepath)[0]
        Path(path).mkdir(parents=True, exist_ok=True)
