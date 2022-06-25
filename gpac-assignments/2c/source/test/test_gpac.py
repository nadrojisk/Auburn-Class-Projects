""" Module for test code for gpac module. """
import copy
import pytest
import gpac
import random

# pylint: disable=protected-access
# pylint: disable=missing-function-docstring


def test_parse_map():
    width, height, board = gpac.GPac._parse_map('maps/map0.txt')
    assert width == 35
    assert height == 20

    expected_board = [
        ['~', '~', '~', '~', '~', '~', '~', '~', '~', '~', '~', '~', '~', '~', '~', '~', '#', '#',
         '#', '~', '~', '~', '~', '~', '~', '~', '~', '~', '~', '~', '~', '~', '~', '~', '~'],
        ['~', '#', '#', '#', '~', '#', '#', '~', '#', '~', '#', '#', '#', '~', '#', '~', '#', '#',
         '#', '~', '#', '~', '#', '#', '#', '~', '#', '~', '#', '#', '~', '#', '#', '#', '~'],
        ['~', '#', '#', '#', '~', '~', '~', '~', '~', '~', '#', '#', '#', '~', '#', '~', '#', '#',
         '#', '~', '#', '~', '#', '#', '#', '~', '~', '~', '~', '~', '~', '#', '#', '#', '~'],
        ['~', '~', '~', '~', '~', '#', '#', '#', '#', '#', '#', '#', '#', '~', '#', '~', '~', '~',
         '~', '~', '#', '~', '#', '#', '#', '#', '#', '#', '#', '#', '~', '~', '~', '~', '~'],
        ['~', '#', '#', '~', '#', '#', '#', '#', '#', '#', '#', '#', '#', '~', '#', '~', '#', '#',
         '#', '~', '#', '~', '#', '#', '#', '#', '#', '#', '#', '#', '#', '~', '#', '#', '~'],
        ['~', '~', '~', '~', '~', '#', '#', '#', '#', '#', '#', '#', '#', '~', '#', '~', '#', '#',
         '#', '~', '#', '~', '#', '#', '#', '#', '#', '#', '#', '#', '~', '~', '~', '~', '~'],
        ['~', '#', '#', '#', '~', '~', '~', '~', '#', '#', '#', '#', '#', '~', '#', '~', '#', '#',
         '#', '~', '#', '~', '#', '#', '#', '#', '#', '~', '~', '~', '~', '#', '#', '#', '~'],
        ['~', '#', '~', '~', '~', '#', '#', '~', '#', '#', '#', '#', '#', '~', '~', '~', '~', '~',
         '~', '~', '~', '~', '#', '#', '#', '#', '#', '~', '#', '#', '~', '~', '~', '#', '~'],
        ['~', '#', '~', '#', '#', '#', '#', '~', '#', '#', '#', '#', '#', '~', '#', '#', '~', '#',
         '~', '#', '#', '~', '#', '#', '#', '#', '#', '~', '#', '#', '#', '#', '~', '#', '~'],
        ['~', '#', '~', '#', '#', '#', '#', '~', '~', '~', '~', '~', '~', '~', '~', '~', '~', '#',
         '~', '~', '~', '~', '~', '~', '~', '~', '~', '~', '#', '#', '#', '#', '~', '#', '~'],
        ['~', '~', '~', '#', '#', '#', '#', '#', '#', '#', '#', '#', '~', '#', '#', '#', '~', '#',
         '~', '#', '#', '#', '~', '#', '#', '#', '#', '#', '#', '#', '#', '#', '~', '~', '~'],
        ['#', '~', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '~', '#', '#', '#', '~', '#',
         '~', '#', '#', '#', '~', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '~', '#'],
        ['#', '~', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '~', '#', '#', '#', '~', '#',
         '~', '#', '#', '#', '~', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '~', '#'],
        ['#', '~', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '~', '~', '~', '~', '~', '#',
         '~', '~', '~', '~', '~', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '~', '#'],
        ['#', '~', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '~', '~', '~',
         '~', '~', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '~', '#'],
        ['~', '~', '~', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '~', '#', '#',
         '#', '~', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '~', '~', '~'],
        ['~', '#', '~', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '~', '#', '#',
         '#', '~', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '#', '~', '#', '~'],
        ['~', '#', '~', '~', '~', '#', '~', '~', '~', '#', '#', '#', '#', '#', '#', '~', '#', '#',
         '#', '~', '#', '#', '#', '#', '#', '#', '~', '~', '~', '#', '~', '~', '~', '#', '~'],
        ['~', '#', '#', '#', '~', '#', '~', '#', '~', '~', '~', '~', '~', '#', '#', '~', '#', '#',
         '#', '~', '#', '#', '~', '~', '~', '~', '~', '#', '~', '#', '~', '#', '#', '#', '~'],
        ['~', '~', '~', '~', '~', '~', '~', '~', '~', '#', '#', '#', '~', '~', '~', '~', '~', '~',
         '~', '~', '~', '~', '~', '#', '#', '#', '~', '~', '~', '~', '~', '~', '~', '~', '~']]
    assert expected_board == board


def test_parse_map_nonexistent():
    width, height, board = gpac.GPac._parse_map('none')

    assert width == 0
    assert height == 0
    assert board == []


def test_place_pills():
    instance = gpac.GPac('maps/map0.txt', .05, 0, 0, 10)
    og_board = copy.deepcopy(instance.board)
    instance._place_pills()
    assert og_board != instance.board

    pill_count = 0
    for row in instance.board:
        if gpac.PILL in row:
            pill_count += 1
    assert pill_count >= 1


def test_place_pills_at_least_one():
    instance = gpac.GPac('maps/map0.txt', 0, 0, 0, 10)

    pill_count = 0
    for row in instance.board:
        if gpac.PILL in row:
            pill_count += 1
    assert pill_count == 1


def test_place_pills_bad():
    with pytest.raises(Exception):
        gpac.GPac('maps/map0.txt', 50, 0, 0, 0)


def test_place_fruit():
    instance = gpac.GPac('maps/map0.txt', .50, 1, 0, 10)
    instance._place_fruit()

    random.seed(1)

    fruit_count = 0
    for row in instance.board:
        if gpac.FRUIT in row:
            fruit_count += 1
    assert fruit_count == 1


def test_place_fruit_already_exists():
    instance = gpac.GPac('maps/map0.txt', .50, 1, 0, 10)

    instance._place_fruit()

    fruit_count = 0
    for row in instance.board:
        if gpac.FRUIT in row:
            fruit_count += 1
    assert fruit_count == 1


def test_place_fruit_bad():
    with pytest.raises(Exception):
        gpac.GPac('maps/map0.txt', .50, 2, 0, 10)


def test_neg_index_to_positive():
    assert gpac.GPac.neg_index_to_positive(-1, 20) == 19


def test_neg_index_to_positive_pos():
    assert gpac.GPac.neg_index_to_positive(1, 20) == 1


def test_convert_coord():
    instance = gpac.GPac('./maps/map0.txt', .50, .5, 0, 10)
    assert list(instance._convert_coordinates([0, 0])) == [0, 19]


def test_convert_coord_2():
    instance = gpac.GPac('./maps/map0.txt', .50, .5, 0, 10)
    assert list(instance._convert_coordinates([18, 0])) == [0, 1]


def test_convert_coord_3():
    instance = gpac.GPac('./maps/map0.txt', .50, .5, 0, 10)
    assert list(instance._convert_coordinates([18, 3])) == [3, 1]


def test_move_pacman():
    instance = gpac.GPac('maps/map0.txt', .50, .5, 0, 10)
    assert instance.locations[gpac.PACMAN] == [0, 0]
    instance.move(gpac.DOWN, gpac.PACMAN)
    assert instance.locations[gpac.PACMAN] == [1, 0]


def test_ghost_collision():
    instance = gpac.GPac('maps/map0.txt', .50, .5, 0, 10)
    instance.locations[gpac.GHOST[0]] = [1, 0]

    instance.move(gpac.DOWN, gpac.PACMAN)
    assert instance._pacman_collision() == gpac.GHOST_COLLISION


def test_pill_collision():
    instance = gpac.GPac('maps/map0.txt', 0, 0, 0, 10)
    instance.locations[gpac.PILL][0] = [1, 0]
    instance.board[1][0] = 'p'

    instance.move(gpac.DOWN, gpac.PACMAN)
    instance._pacman_collision()
    assert instance.consumed['pill'] == 1

    for pill in instance.locations[gpac.PILL]:
        assert pill != [1, 0]


def test_fruit_collision():
    instance = gpac.GPac('maps/map0.txt', 0, 0, 0, 10)
    instance.locations[gpac.FRUIT] = [1, 0]

    instance.move(gpac.DOWN, gpac.PACMAN)
    instance._pacman_collision()
    assert instance.consumed['fruit'] == 1

    assert instance.locations[gpac.FRUIT] == []


# def test_turn():
#     instance = gpac.GPac('maps/map0.txt', 0, 0, 0, 10)
#     instance.turn(gpac.DOWN, gpac.LEFT, gpac.LEFT, gpac.LEFT)

def test_score_calculation_immediate():
    instance = gpac.GPac('maps/map0.txt', .5, 0.01, 10, 2)
    assert instance._calculate_score() == 0


def test_score_calculation_all_pills():
    instance = gpac.GPac('maps/map0.txt', .5, 0.01, 10, 2)
    instance.consumed['pill'] = 142
    assert instance._calculate_score() == 199


def test_score_calculation_all_but_one_pill():
    instance = gpac.GPac('maps/map0.txt', .5, 0.01, 10, 2)
    instance.consumed['pill'] = 141
    assert instance._calculate_score() == 100


def test_score_calculation_all_pills_no_time():
    instance = gpac.GPac('maps/map0.txt', .5, 0.01, 10, 2)
    instance.consumed['pill'] = 142
    instance.time_elapsed = instance.time
    assert instance._calculate_score() == 100
