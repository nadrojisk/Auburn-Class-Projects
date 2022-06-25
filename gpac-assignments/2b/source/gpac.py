""" Module that implements map parsing and game logic """

import os
import random
import copy
import math
from utilities import MyException

# global constants

# unit types
WALL = '#'
EMPTY_CELL = '~'
PILL = "p"
GHOST = ["1", "2", "3"]
PACMAN = "m"
FRUIT = "f"

# directions
UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'
HOLD = 'hold'

# errors
ERROR_PILL_DENSITY = -1
ERROR_FRUIT_CHANCE = -2
ERROR_NOT_MOVED = -3
ERROR_NO_ERROR = 0

# collisions
GHOST_COLLISION = 10
FRUIT_COLLISION = 20
PILL_COLLISION = 30
NO_COLLISION = 40


class GPac():
    """ GPac class. Defines functionality for the Pac-Man Game logic."""

    # pylint: disable=too-many-instance-attributes

    ###################################################################
    #######################     Core    ###############################
    ###################################################################

    def __init__(self, filename, pill_chance, fruit_chance, fruit_score, time_multiplier):
        # pylint: disable=too-many-arguments
        width, height, board = self._parse_map(filename)
        self.world_contents = f'{width}\n{height}\n'
        self.width = width    # x
        self.height = height  # y
        self.board = board

        self.chances = {}
        self.chances['pill'] = pill_chance
        self.chances['fruit'] = fruit_chance

        self.level_filename = filename

        self.locations = {}
        self.locations[PACMAN] = self._place_pacman()
        self.locations = {**self.locations, **self._place_ghosts()}
        self.locations[WALL] = self._read_walls()
        self.locations[PILL] = self._place_pills()
        self.locations[FRUIT] = self._place_fruit()

        self.total_pills = len(self.locations[PILL])

        self.fruit_score = fruit_score
        self.time_multiplier = time_multiplier

        self.time = width * height * self.time_multiplier
        self.time_elapsed = 0

        self.consumed = {}
        self.consumed['pill'] = 0
        self.consumed['fruit'] = 0

        self.is_gameover = False

        self.pman_turn = False
        self.ghost1_turn = False
        self.ghost2_turn = False
        self.ghost3_turn = False

        self._log_turn()

    def _read_walls(self):
        """ Adds walls to log file """

        walls = []
        for row, _ in enumerate(self.board):
            for column, _ in enumerate(self.board[row]):
                cell = self.board[row][column]
                if cell == WALL:
                    walls.append([row, column])
                    self._place([row, column], '#')
                    # redundant but allows walls to be logged
        return walls

    def turn(self):
        """ Handles a "turn". Pac-Man and Ghosts move.
        If Pac-Man collides with ghosts game ends.
        If Pac-Man collides with a pill or a fruit it is eaten.

        At the end of turn it is checked to see if the game is over.
        Additionally, it is checked to see if the game is over first
        thing just in case the function is called after the game is over.
        """

        if self.is_gameover:
            return self._calculate_score(), self.world_contents

        if self.pman_turn and self.ghost1_turn and self.ghost2_turn and self.ghost3_turn:
            self._log_turn()

            self.pman_turn = False
            self.ghost1_turn = False
            self.ghost2_turn = False
            self.ghost3_turn = False

            if self.time == self.time_elapsed or self.total_pills == self.consumed['pill']:
                self.is_gameover = True
                return self._calculate_score(), self.world_contents

            # replace fruit if fruit is gone
            self.locations[FRUIT] = self._place_fruit()

        return self._calculate_score(), self.world_contents

    ###################################################################
    #####################     Placement    ############################
    ###################################################################

    def _place_pacman(self):
        """ Places pacman. Returns location to be added to location dict"""

        self._place([0, 0], PACMAN)
        return [0, 0]

    def _place_ghosts(self):
        """ Place ghosts on board. Returns dict to be merged with locations """
        locations = {}

        spots = [[-1, -1],
                 [-1, -1],
                 [-1, -1]]

        for i, spot in enumerate(spots):
            y_loc = self.neg_index_to_positive(spot[0], self.height)
            x_loc = self.neg_index_to_positive(spot[1], self.width)

            locations[GHOST[i]] = [y_loc, x_loc]
            self._place([y_loc, x_loc], GHOST[i])
        return locations

    def _place_pills(self):
        """ Places pills in empty cells based on pill_chance value. """
        if self.chances['pill'] > 1:
            raise MyException(
                "Error: Fruit Chance should be in the range [0,1]")

        pills = []
        walls = sum([row.count(WALL) for row in self.board])
        cells = len(self.board) * len(self.board[0])
        total_pills = math.floor(self.chances['pill'] * (cells - 1 - walls))

        pill_count = 0
        while pill_count != total_pills:
            for row_count, row in enumerate(self.board):
                if pill_count == total_pills:
                    break
                for column_count, cell in enumerate(row):
                    if pill_count == total_pills:
                        break
                    if cell != WALL and cell != PILL and \
                            not (row_count == 0 and column_count == 0):
                        rng = random.random()
                        if rng <= self.chances['pill']:
                            self._place([row_count, column_count], PILL)
                            pills.append([row_count, column_count])
                            pill_count += 1

        # has to have at least one pill
        if pill_count == 0:
            while pill_count != 1:
                width = len(self.board[0])
                height = len(self.board)
                rand_row = random.randint(0, height - 1)
                rand_column = random.randint(0, width - 1)

                if self.board[rand_row][rand_column] == EMPTY_CELL and \
                        not (rand_row == 0 and rand_column == 0):

                    self._place([rand_row, rand_column], PILL)
                    pills.append([rand_row, rand_column])
                    break

        return pills

    def _place_fruit(self):
        """ Place fruit on board based on chance value. If fruit already
        exists do not place anything as only one fruit can be on the board at a time. """

        if self.chances['fruit'] > 1:
            raise MyException(
                "Error: Fruit Chance should be in the range [0,1]")

        # check if board has fruit
        if self.locations.get(FRUIT, None):
            return self.locations.get(FRUIT)

        rng = random.random()
        if rng <= self.chances['fruit']:
            # place fruit
            width = len(self.board[0])
            height = len(self.board)

            # loop until a location that is free is found
            while True:
                rand_row = random.randint(0, height - 1)
                rand_column = random.randint(0, width - 1)

                location = self.board[rand_row][rand_column]

                if location == EMPTY_CELL or location in GHOST:
                    self._place([rand_row, rand_column], FRUIT)
                    return [rand_row, rand_column]

    ###################################################################
    #####################   Unit Interaction    #######################
    ###################################################################

    def move(self, direction, unit_type):
        """ Moves a unit in a cardinal direction. If the unit
        cannot move in that direction nothing happens
        """
        if self.is_gameover:
            return

        current_position = self.locations[unit_type]
        new_position = self.cardinal_to_location(direction, current_position, unit_type)

        # update position in dict, move to new position, remove old position
        self.locations[unit_type] = new_position
        self._place(new_position, unit_type)

        # check for collisions
        if self._collisions(unit_type) == GHOST_COLLISION:
            self.is_gameover = True

        if unit_type == PACMAN:
            self.pman_turn = True
        elif unit_type == GHOST[0]:
            self.ghost1_turn = True
        elif unit_type == GHOST[1]:
            self.ghost2_turn = True
        elif unit_type == GHOST[2]:
            self.ghost3_turn = True

    def _remove(self, location):
        """ Removes a unit from the board. """
        self.board[location[0]][location[1]] = EMPTY_CELL

    def _place(self, location, unit_type, log=True):
        """ Places unit on board and log to file.

        location - unit's location
        unit_type - unit type (i.e. for pacman it would be 'p'
        """
        # only place pills / fruit
        if unit_type == PILL or unit_type == FRUIT:
            self.board[location[0]][location[1]] = unit_type

        if log:
            # convert python's negative index to positives for logging
            location[0] = self.neg_index_to_positive(location[0], self.height)
            location[1] = self.neg_index_to_positive(location[1], self.width)

            # convert coordinates as world file should have origin in bottom left not top right
            x_loc, y_loc = self._convert_coordinates(location)
            self._log_world(unit_type, str(x_loc), str(y_loc))

    def _pacman_collision(self):
        """ handles pacman collisions """

        loc = self.locations[PACMAN]
        for i in range(3):
            if loc == self.locations[GHOST[i]]:
                return GHOST_COLLISION  # GAMEOVER

        # collides with pill
        if self.board[loc[0]][loc[1]] == PILL:
            self.consumed['pill'] += 1
            self.locations[PILL].remove(loc)
            self._remove(loc)
            return PILL_COLLISION

        # collides with fruit
        if self.locations[FRUIT] == loc:
            self.consumed['fruit'] += 1
            self.locations[FRUIT] = []
            self._remove(loc)
            return FRUIT_COLLISION

        return NO_COLLISION

    def _ghost_collision(self, unit_type):
        """ Logic to see if ghost unit is colliding with Pac-Man """

        # ensure type passed is a ghost
        if unit_type not in GHOST:
            return NO_COLLISION

        if self.locations[unit_type] == self.locations[PACMAN]:
            return GHOST_COLLISION
        return NO_COLLISION

    def _collisions(self, unit_type):
        """ handles pacman collisions """

        if unit_type == PACMAN:
            return self._pacman_collision()
        else:
            return self._ghost_collision(unit_type)

    def get_all_spots_around_cell(self, cell):
        """ Gets all spots around the passed cell.

        Does not look at any game logic just gets the raw cells around a cell.
        """

        possible_spots = [[cell[0] + 1, cell[1]],
                          [cell[0], cell[1] + 1],
                          [cell[0] - 1, cell[1]],
                          [cell[0], cell[1] - 1], cell]
        final_spots = []
        for spot in possible_spots:
            if spot[0] < 0 or spot[1] < 0:
                continue
            if spot[0] < self.height and spot[1] < self.width:
                final_spots.append(spot)
        return final_spots

    def get_spots_around_unit(self, unit_type):
        """ Gets all legal spots around the passed cell.

        For instance ghosts cannot move through ghosts so there is
        special logic for that unit.
        """

        cell = self.locations[unit_type]
        spots = self.get_all_spots_around_cell(cell)
        final_spots = []
        for spot in spots:
            if unit_type in GHOST:
                if cell == spot:
                    continue
            if self.board[spot[0]][spot[1]] == '#':
                continue

            final_spots.append(spot)

        return final_spots

    def get_moves_for_unit(self, unit_type):
        """" Gets possible moves for a unit"""

        unit_loc = self.locations[unit_type]
        coords_to_move_to = self.get_spots_around_unit(unit_type)
        movements = []
        if not coords_to_move_to:
            movements.append('BAD')
        else:
            for coord in coords_to_move_to:
                movements.append(self.location_to_cardinal(unit_loc, coord))
        return movements

    ###################################################################
    #########################   Utilities    ##########################
    ###################################################################

    @staticmethod
    def neg_index_to_positive(value, max_val):
        """ Converts negative index value to positive"""
        return value % max_val

    @staticmethod
    def location_to_cardinal(unit_loc, coord):
        """ Translates location to a cardinal direction

        unit_loc: location of unit that is moving
        coord: location that the unit is moving to
        """

        if unit_loc[0] - 1 == coord[0]:
            return UP
        if unit_loc[0] + 1 == coord[0]:
            return DOWN
        if unit_loc[1] - 1 == coord[1]:
            return LEFT
        if unit_loc[1] + 1 == coord[1]:
            return RIGHT
        if unit_loc == coord:
            return HOLD
        return None

    @staticmethod
    def cardinal_to_location(direction, current_position, unit_type):
        """ Translates cardinal direction to location

        direction - cardinal direction
        current_position - current location of unit
        unit_type - type of unit in question
        """

        new_position = copy.deepcopy(current_position)
        if direction == UP:
            new_position[0] -= 1
        elif direction == DOWN:
            new_position[0] += 1
        elif direction == LEFT:
            new_position[1] -= 1
        elif direction == RIGHT:
            new_position[1] += 1
        elif direction == HOLD and unit_type == PACMAN:
            pass
        return new_position

    @staticmethod
    def _parse_map(filename):
        """ Parses provided file and returns width, height, and game board. """

        if os.path.exists(filename):
            with open(filename) as file:
                file_contents = file.read()
            file_lines = file_contents.split('\n')
            width, height = [int(val)
                             for val in file_lines[0].split(' ')]

            board_str = file_lines[1:]
            board = [list(line) for line in board_str]
            return width, height, board
        return 0, 0, []

    def _convert_coordinates(self, coordinates):
        """ Converts input coordinates as if the origin of the board was bottom left """
        return coordinates[1], len(self.board) - coordinates[0] - 1

    def _calculate_score(self):
        """ Calculates score of game. """

        score = 0
        score += math.ceil((self.consumed['pill'] / self.total_pills) * 100)
        score += self.consumed['fruit'] * self.fruit_score
        if self.consumed['pill'] == self.total_pills:
            score += math.floor(((self.time - self.time_elapsed) / self.time) * 100)
        return score

    def print_board(self):
        """ Helper method that prints off the game board in a human readable way. """

        os.system('clear')
        print(f"GPac by Jordan Sosnowski \t{self.time - self.time_elapsed}")
        print('-' * (self.width + 1))

        board = copy.deepcopy(self.board)
        pacman_loc = self.locations[PACMAN]
        board[pacman_loc[0]][pacman_loc[1]] = PACMAN

        ghost_1_loc = self.locations[GHOST[0]]
        board[ghost_1_loc[0]][ghost_1_loc[1]] = GHOST[0]

        ghost_2_loc = self.locations[GHOST[1]]
        board[ghost_2_loc[0]][ghost_2_loc[1]] = GHOST[1]

        ghost_3_loc = self.locations[GHOST[2]]
        board[ghost_3_loc[0]][ghost_3_loc[1]] = GHOST[2]

        for row in board:
            row_str = ''.join(row)
            row_str = row_str.replace('~', ' ')
            row_str = row_str.replace('1', '▼')
            row_str = row_str.replace('2', '▼')
            row_str = row_str.replace('3', '▼')
            row_str = row_str.replace('m', '○')
            print('|' + row_str + '|')
        print('-' * (self.width + 1))

    ###################################################################
    ##########################   Log    ###############################
    ###################################################################
    def _log_world(self, log_type, *args):
        """ Logs info to buffer with the following format:
        log_type args[0] args[1] ... args[n]

        log_type: type of unit being logged
        args: list of args to log related to the log_type
        """

        log_type = log_type.replace('#', 'w')
        self.world_contents += ' '.join([log_type, *args, '\n'])

    def _log_turn(self):
        """ Logs current turn. Calculates score and passses to log_world."""

        current_score = self._calculate_score()
        self._log_world('t', str(self.time - self.time_elapsed), str(current_score))
        self.time_elapsed += 1
