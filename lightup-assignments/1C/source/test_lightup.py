import lightup
import numpy as np


def test_parse_problem():

    actual_columns, actual_rows, actual_black_cells = lightup.parse_problem_file(
        'problems/bc1.lup')

    expected_columns = 6
    expected_rows = 6
    expected_black_cells = [[4, 6, 1], [1, 5, 0],
                            [5, 5, 5], [5, 4, 1], [1, 3, 5],
                            [5, 1, 2], [6, 1, 5]]

    assert actual_columns == expected_columns
    assert actual_rows == expected_rows
    assert actual_black_cells == expected_black_cells


def test_problem_creation():
    columns = 5
    rows = 5
    black_cells = [[2, 3, 2], [2, 5, 5], [3, 2, 0], [3, 5, 0], [4, 4, 5]]

    actual_instance = lightup.create_problem_instance(
        columns, rows, black_cells)

    expected_instance = np.zeros([5, 5], dtype=int)
    expected_instance.fill(-1)
    expected_instance[1][2] = 2
    expected_instance[1][4] = 5
    expected_instance[2][1] = 0
    expected_instance[2][4] = 0
    expected_instance[3][3] = 5

    expected_instance = np.rot90(expected_instance)

    assert (actual_instance == expected_instance).all()


def test_create_board():

    actual_board = lightup.create_board('./problems/bc1.lup')

    expected_instance = np.zeros([6, 6], dtype=int)
    expected_instance.fill(-1)
    expected_instance = np.rot90(expected_instance)

    expected_instance[1][0] = 0
    expected_instance[0][3] = 1
    expected_instance[1][4] = 5
    expected_instance[3][0] = 5
    expected_instance[2][4] = 1
    expected_instance[5][4] = 2
    expected_instance[5][5] = 5

    assert (actual_board == expected_instance).all()


def test_calculate_completion():
    board = np.zeros([5, 5], dtype=int)
    board.fill(-1)
    board[1][2] = 2
    board[1][4] = 5
    board[2][1] = 0
    board[2][4] = 0
    board[3][3] = 5

    board = np.rot90(board)

    board[2][0] = lightup.BULB
    board[0][4] = lightup.BULB
    board[1][1] = lightup.BULB
    board[2][3] = lightup.BULB
    board[4][1] = lightup.BULB

    board[1][0] = lightup.LIT
    board[0][0] = lightup.LIT
    board[3][0] = lightup.LIT
    board[4][0] = lightup.LIT
    board[3][1] = lightup.LIT
    board[1][2] = lightup.LIT
    board[2][2] = lightup.LIT
    board[4][2] = lightup.LIT
    board[0][3] = lightup.LIT
    board[3][3] = lightup.LIT
    board[4][3] = lightup.LIT
    board[1][4] = lightup.LIT
    board[2][4] = lightup.LIT
    board[3][4] = lightup.LIT
    board[4][4] = lightup.LIT

    fitness = lightup.calculate_completion(board)
    assert fitness == 100


def test_calculate_completion_ignore_black_cells():
    board = np.zeros([5, 5], dtype=int)
    board.fill(-1)
    board[1][2] = 2
    board[1][4] = 5
    board[2][1] = 0
    board[2][4] = 0
    board[3][3] = 5

    board = np.rot90(board)

    board[2][0] = lightup.LIT
    board[0][4] = lightup.BULB
    board[1][1] = lightup.BULB
    board[2][3] = lightup.BULB
    board[4][1] = lightup.BULB

    board[1][0] = lightup.LIT
    board[0][0] = lightup.LIT
    board[3][0] = lightup.LIT
    board[4][0] = lightup.LIT
    board[3][1] = lightup.LIT
    board[1][2] = lightup.LIT
    board[2][2] = lightup.LIT
    board[4][2] = lightup.LIT
    board[0][3] = lightup.LIT
    board[3][3] = lightup.LIT
    board[4][3] = lightup.LIT
    board[1][4] = lightup.LIT
    board[2][4] = lightup.LIT
    board[3][4] = lightup.LIT
    board[4][4] = lightup.LIT

    fitness = lightup.calculate_completion(board)
    assert fitness == 100


def test_check_black_cells():
    board = np.zeros([5, 5], dtype=int)
    board.fill(-1)
    board[1][2] = 2
    board[1][4] = 5
    board[2][1] = 0
    board[2][4] = 0
    board[3][3] = 5

    board = np.rot90(board)

    board[0][4] = lightup.BULB
    board[1][1] = lightup.BULB
    board[2][3] = lightup.BULB
    board[4][1] = lightup.BULB

    board[2][0] = lightup.LIT

    board[0][0] = lightup.LIT
    board[1][0] = lightup.LIT
    board[3][0] = lightup.LIT
    board[4][0] = lightup.LIT
    board[3][1] = lightup.LIT
    board[1][2] = lightup.LIT
    board[2][2] = lightup.LIT
    board[4][2] = lightup.LIT
    board[0][3] = lightup.LIT
    board[3][3] = lightup.LIT
    board[4][3] = lightup.LIT
    board[1][4] = lightup.LIT
    board[2][4] = lightup.LIT
    board[3][4] = lightup.LIT
    board[4][4] = lightup.LIT
    black_cell_dict = lightup.check_black_cells(board, False)
    assert black_cell_dict == {2: [1]}


def test_calculate_completion_bad_intersection():
    board = np.zeros([5, 5], dtype=int)
    board.fill(-1)
    board[1][2] = 2
    board[1][4] = 5
    board[2][1] = 0
    board[2][4] = 0
    board[3][3] = 5

    board = np.rot90(board)

    board[2][0] = lightup.BULB
    board[0][4] = lightup.BULB
    board[1][1] = lightup.BULB
    board[2][3] = lightup.BULB
    board[4][1] = lightup.BULB

    board[0][0] = lightup.BULB

    board[1][0] = lightup.LIT
    board[3][0] = lightup.LIT
    board[4][0] = lightup.LIT
    board[3][1] = lightup.LIT
    board[1][2] = lightup.LIT
    board[2][2] = lightup.LIT
    board[4][2] = lightup.LIT
    board[0][3] = lightup.LIT
    board[3][3] = lightup.LIT
    board[4][3] = lightup.LIT
    board[1][4] = lightup.LIT
    board[2][4] = lightup.LIT
    board[3][4] = lightup.LIT
    board[4][4] = lightup.LIT

    fitness = lightup.calculate_completion(board)
    assert fitness == 100


def test_check_intersection():
    board = np.zeros([5, 5], dtype=int)
    board.fill(-1)
    board[1][2] = 2
    board[1][4] = 5
    board[2][1] = 0
    board[2][4] = 0
    board[3][3] = 5

    board = np.rot90(board)

    board[2][0] = lightup.BULB
    board[0][4] = lightup.BULB
    board[1][1] = lightup.BULB
    board[2][3] = lightup.BULB
    board[4][1] = lightup.BULB

    board[0][0] = lightup.BULB

    board[1][0] = lightup.LIT
    board[3][0] = lightup.LIT
    board[4][0] = lightup.LIT
    board[3][1] = lightup.LIT
    board[1][2] = lightup.LIT
    board[2][2] = lightup.LIT
    board[4][2] = lightup.LIT
    board[0][3] = lightup.LIT
    board[3][3] = lightup.LIT
    board[4][3] = lightup.LIT
    board[1][4] = lightup.LIT
    board[2][4] = lightup.LIT
    board[3][4] = lightup.LIT
    board[4][4] = lightup.LIT

    intersections_dict = lightup.check_intersections(board)
    assert intersections_dict == {'[ 10 100  10 100 100]': [1]}


def test_check_intersection_black_cell_interrupt():
    board = np.zeros([5, 5], dtype=int)
    board.fill(-1)

    board[1][2] = 2
    board[1][4] = 5
    board[2][1] = 0
    board[2][4] = 0
    board[3][3] = 5

    board = np.rot90(board)

    board[1][0] = 0

    board[2][0] = lightup.BULB
    board[0][4] = lightup.BULB
    board[1][1] = lightup.BULB
    board[2][3] = lightup.BULB
    board[4][1] = lightup.BULB

    board[0][0] = lightup.BULB

    board[3][0] = lightup.LIT
    board[4][0] = lightup.LIT
    board[3][1] = lightup.LIT
    board[1][2] = lightup.LIT
    board[2][2] = lightup.LIT
    board[4][2] = lightup.LIT
    board[0][3] = lightup.LIT
    board[3][3] = lightup.LIT
    board[4][3] = lightup.LIT
    board[1][4] = lightup.LIT
    board[2][4] = lightup.LIT
    board[3][4] = lightup.LIT
    board[4][4] = lightup.LIT

    intersections_dict = lightup.check_intersections(board)
    assert intersections_dict == {}


def test_check_intersection_black_cell_interrupt_2():
    board = np.zeros([5, 5], dtype=int)
    board.fill(-1)

    board[1][2] = 2
    board[1][4] = 5
    board[2][1] = 0
    board[2][4] = 0
    board[3][3] = 5

    board = np.rot90(board)

    board[1][0] = 0

    board[2][0] = lightup.BULB
    board[0][4] = lightup.BULB
    board[1][1] = lightup.BULB
    board[2][3] = lightup.BULB
    board[4][1] = lightup.BULB

    board[0][0] = lightup.BULB
    board[3][0] = lightup.BULB

    board[4][0] = lightup.LIT
    board[3][1] = lightup.LIT
    board[1][2] = lightup.LIT
    board[2][2] = lightup.LIT
    board[4][2] = lightup.LIT
    board[0][3] = lightup.LIT
    board[3][3] = lightup.LIT
    board[4][3] = lightup.LIT
    board[1][4] = lightup.LIT
    board[2][4] = lightup.LIT
    board[3][4] = lightup.LIT
    board[4][4] = lightup.LIT

    intersections_dict = lightup.check_intersections(board)
    assert intersections_dict == {'[ 10   0  10  10 100]': [1]}


def test_calculate_completion_bad_cell_count():
    board = np.zeros([5, 5], dtype=int)
    board.fill(-1)
    board[1][2] = 2
    board[1][4] = 5
    board[2][1] = 0
    board[2][4] = 0
    board[3][3] = 5

    board = np.rot90(board)

    board[0][4] = lightup.BULB
    board[1][1] = lightup.BULB
    board[2][3] = lightup.BULB
    board[4][1] = lightup.BULB

    board[2][0] = lightup.LIT

    board[0][0] = lightup.LIT
    board[1][0] = lightup.LIT
    board[3][0] = lightup.LIT
    board[4][0] = lightup.LIT
    board[3][1] = lightup.LIT
    board[1][2] = lightup.LIT
    board[2][2] = lightup.LIT
    board[4][2] = lightup.LIT
    board[0][3] = lightup.LIT
    board[3][3] = lightup.LIT
    board[4][3] = lightup.LIT
    board[1][4] = lightup.LIT
    board[2][4] = lightup.LIT
    board[3][4] = lightup.LIT
    board[4][4] = lightup.LIT

    fitness = lightup.calculate_completion(board)
    assert fitness == 100


def test_calculate_completion_bad_not_all_lit():
    board = np.zeros([5, 5], dtype=int)
    board.fill(-1)
    board[1][2] = 2
    board[1][4] = 5
    board[2][1] = 0
    board[2][4] = 0
    board[3][3] = 5

    board = np.rot90(board)

    board[2][0] = lightup.BULB
    board[0][4] = lightup.BULB
    board[1][1] = lightup.BULB
    board[2][3] = lightup.BULB
    board[4][1] = lightup.BULB

    board[1][0] = lightup.LIT
    board[0][0] = lightup.LIT
    board[3][0] = lightup.LIT

    board[3][1] = lightup.LIT
    board[1][2] = lightup.LIT
    board[2][2] = lightup.LIT
    board[4][2] = lightup.LIT
    board[0][3] = lightup.LIT
    board[3][3] = lightup.LIT
    board[4][3] = lightup.LIT
    board[1][4] = lightup.LIT
    board[2][4] = lightup.LIT
    board[3][4] = lightup.LIT
    board[4][4] = lightup.LIT

    fitness = lightup.calculate_completion(board)
    assert fitness == 95


def test_place_bulb_simple():
    actual_board = np.zeros([5, 5], dtype=int)
    actual_board.fill(-1)

    actual_board = lightup.place_bulb(actual_board, (0, 4))

    expected_board = np.zeros([5, 5], dtype=int)
    expected_board.fill(-1)
    expected_board[0, 4] = lightup.BULB
    expected_board[0, 3] = lightup.LIT
    expected_board[0, 2] = lightup.LIT
    expected_board[0, 1] = lightup.LIT
    expected_board[0, 0] = lightup.LIT
    expected_board[1, 4] = lightup.LIT
    expected_board[2, 4] = lightup.LIT
    expected_board[3, 4] = lightup.LIT
    expected_board[4, 4] = lightup.LIT

    assert (actual_board == expected_board).all()


def test_place_bulb_a_black_cell():
    expected_board = np.zeros([5, 5], dtype=int)
    expected_board.fill(-1)
    expected_board[1][2] = 2
    expected_board[1][4] = 5
    expected_board[2][1] = 0
    expected_board[2][4] = 0
    expected_board[3][3] = 5

    expected_board = np.rot90(expected_board)

    expected_board[0, 4] = lightup.BULB

    expected_board[0, 3] = lightup.LIT
    expected_board[1, 4] = lightup.LIT
    expected_board[2, 4] = lightup.LIT
    expected_board[3, 4] = lightup.LIT
    expected_board[4, 4] = lightup.LIT

    actual_board = np.zeros([5, 5], dtype=int)
    actual_board.fill(-1)
    actual_board[1][2] = 2
    actual_board[1][4] = 5
    actual_board[2][1] = 0
    actual_board[2][4] = 0
    actual_board[3][3] = 5

    actual_board = np.rot90(actual_board)
    actual_board = lightup.place_bulb(actual_board, (0, 4))

    assert (actual_board == expected_board).all()


def test_around_cell():

    cells = lightup.get_spots_around_cell([0, 0], [5, 5])
    assert cells == ((1, 0), (0, 1))

    cells = lightup.get_spots_around_cell([1, 1], [3, 3])
    assert cells == ((2, 1), (1, 2), (0, 1), (1, 0))

    cells = lightup.get_spots_around_cell([4, 4], [5, 5])
    assert cells == ((3, 4), (4, 3))
