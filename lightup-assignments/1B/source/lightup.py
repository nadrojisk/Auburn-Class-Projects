"""This module provides an implementation for the lightup game """

import numpy as np

# global types used by the program
NOT_LIT = -1
LIT = 100
BULB = 10
BLACK_CELLS = [0, 1, 2, 3, 4, 5]


def parse_problem_file(filename):
    """Parse file for relevant information needed for program.

    Problem file has the following format
    x
    y

    x1 y1 b1
    x2 y2 b2

    where x is the number of columns
    where y is the number of rows
    x1 y1 is the first coordinate of a black cell and b1 is the number to be
    placed in the cell.

    Keyword arguments:
    filename -- file to parse for problem generation
    """

    with open(filename) as file:
        contents = file.read().strip().split("\n")
        columns = int(contents[1])
        rows = int(contents[0])
        black_cells = [x.split() for x in contents[2:]]

        for cell in black_cells:
            for index, element in enumerate(cell):
                cell[index] = int(element)
    return columns, rows, black_cells


def create_problem_instance(columns, rows, black_cells):
    """Generate board from input parameters.

    columns -- integer representing how many columns are needed
    rows -- integer representing how many rows are needed
    black_cells -- 2D list representing the coordinates and the value placed
                    in the black cells
    """

    instance = np.zeros([columns, rows], dtype=int)
    instance.fill(NOT_LIT)
    for cell in black_cells:
        x_cord = cell[0] - 1
        y_cord = cell[1] - 1
        bulbs = cell[2]
        instance[x_cord][y_cord] = bulbs

    # ensure origin is bottom left not top left
    instance = np.rot90(instance)
    return instance


def create_board(problem_filename):
    """Wraps create_problem_instance and parse_problem_file to generate
    game board.

    problem_filename -- path to problem file
    """
    columns, rows, black_cells = parse_problem_file(
        problem_filename)
    board = create_problem_instance(columns, rows, black_cells)
    return board


def check_intersections(board):
    """ Ensure there are no intersections on the board

    board - RxC numpy array representing the game board, filled with bulbs,
    black cells, and light
    """

    def intersections(space):
        """Ensure there is no intersection of bulb rays.

        space -- list of values for a row / column
        """

        intersection = 0
        for cell in space:
            if cell == BULB:
                intersection += 1
            if intersection >= 2:
                return False
            if cell in BLACK_CELLS:
                intersection = 0
        return True

    shape = board.shape
    for row, column in zip(range(shape[0]), range(shape[1])):

        row = board[row]
        column = board[:, column]

        if not intersections(row) or not intersections(column):
            return 1
    return 0


def get_spots_around_cell(cell, shape):
    """ Gets all legal spots around the passed cell."""

    possible_spots = [(cell[0]+1, cell[1]),
                      (cell[0], cell[1]+1),
                      (cell[0]-1, cell[1]),
                      (cell[0], cell[1]-1)]
    possible_spots = [spot for spot in possible_spots if not (
        spot[0] >= shape[0] or spot[0] < 0) and not (spot[1] >= shape[1] or spot[1] < 0)]

    return tuple(possible_spots)


def check_black_cell_constraint(board, ignore_black_cells=True):
    """Ensures all black cells meet their constraints

    board - RxC numpy array representing the game board, filled with bulbs,
    black cells, and light

    ignore_black_cells - boolean used to determine it black cell constraint should be ignored
    """
    if not ignore_black_cells:
        for value in range(5):
            locations = np.where(board == value)
            list_of_locations = list(zip(locations[0], locations[1]))
            for pair in list_of_locations:
                counter = 0
                possible_spots = get_spots_around_cell(pair, board.shape)
                for spot in possible_spots:

                    contents = board[spot[0]][spot[1]]
                    if contents == BULB:
                        counter += 1
                if counter != value:
                    # bad number of bulbs should equal the value in the black cell
                    return 1
    return 0


def calculate_fitness(board, ignore_black_cells=False):
    """Ensures board is in a complete state returns True if complete.

    board -- RxC numpy array representing the game board, filled with bulbs,
    black cells, and light

    ignore_black_cells -- boolean to allow fitness to ignore the black cell
    surrounding bulb requirement
    """
    # check for black cell satisfaction
    if check_black_cell_constraint(board, ignore_black_cells):
        return 0

    # check to ensure bulbs are not intersecting
    if check_intersections(board):
        return 0

    # ensure there is no non-lit spot on the board
    empty_spots = np.where(board == NOT_LIT)
    empty_spots = list(zip(empty_spots[0], empty_spots[1]))
    lit_spots = np.where(board == LIT)
    lit_spots = list(zip(lit_spots[0], lit_spots[1]))

    bulb_spots = np.where(board == BULB)
    bulb_spots = list(zip(bulb_spots[0], bulb_spots[1]))

    num_of_lit = len(bulb_spots) + len(lit_spots)
    white_cells = len(empty_spots) + num_of_lit
    return max(int(round(num_of_lit / white_cells, 2) * 100), 0)


def place_bulb(board, coordinates):
    """Places bulb on the board at the specified coordinates

    board -- RxC numpy array representing the game board, filled with bulbs,
    black cells, and light

    coordinates -- 2x1 list-like representing where to place the bulb
    """

    # place bulb
    x_cord = coordinates[0]
    y_cord = coordinates[1]
    board[x_cord][y_cord] = BULB

    # generate light
    for x_spot in range(x_cord, board.shape[0]):
        if board[x_spot][y_cord] in BLACK_CELLS:
            break
        if board[x_spot][y_cord] == NOT_LIT:
            board[x_spot][y_cord] = LIT
    for x_spot in range(x_cord)[::-1]:
        if board[x_spot][y_cord] in BLACK_CELLS:
            break
        if board[x_spot][y_cord] == NOT_LIT:
            board[x_spot][y_cord] = LIT

    for y_spot in range(y_cord, board.shape[1]):
        if board[x_cord][y_spot] in BLACK_CELLS:
            break
        if board[x_cord][y_spot] == NOT_LIT:
            board[x_cord][y_spot] = LIT
    for y_spot in range(y_cord)[::-1]:
        if board[x_cord][y_spot] in BLACK_CELLS:
            break
        if board[x_cord][y_spot] == NOT_LIT:
            board[x_cord][y_spot] = LIT

    return board
