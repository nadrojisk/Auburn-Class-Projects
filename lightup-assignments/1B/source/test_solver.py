import individual
import solver as solver
import lightup
import numpy as np


def test_init():
    solve_instance = solver.Solver('./config/test_config.json')
    assert solve_instance.seed is None
    assert solve_instance.num_of_runs == 30
    assert solve_instance.fitness_evals == 10000
    assert solve_instance.log_file == "./logs/a1_run_test.log"
    assert solve_instance.solution_file == "./solutions/a1_solution_test.txt"
    assert solve_instance.evals == []
    assert solve_instance.ignore_black_cells == True


def test_fps():
    solve_instance = solver.Solver('./config/test_config.json')
    fitnesses = [25, 20, 1, 10, 2, 5, 10, 15, 20, 66, 3, 77, 67, 78]
    solve_instance.children = 5
    solve_instance.seed = 1
    solve_instance.set_seed()
    names = ['A', 'B', 'C', 'D', 'E', 'F',
             'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N']

    individuals = individual.Individual.from_list(fitnesses, names)
    actual = solve_instance.fitness_proportional_selection(
        individuals)
    expected = [individual.Individual(10, 'D'),
                individual.Individual(78, 'N'),
                individual.Individual(67, 'M'),
                individual.Individual(20, 'I'),
                individual.Individual(77, 'L'),
                individual.Individual(77, 'L'),
                individual.Individual(67, 'M'),
                individual.Individual(67, 'M'),
                individual.Individual(20, 'B'),
                individual.Individual(25, 'A')]
    assert actual == expected


def test_stochastic():
    solve_instance = solver.Solver('./config/test_config.json')
    fitnesses = [25, 20, 1, 10, 2, 5, 10, 15, 20, 66, 3, 77, 67, 78]
    solve_instance.children = 5
    solve_instance.seed = 1
    solve_instance.set_seed()
    names = ['A', 'B', 'C', 'D', 'E', 'F',
             'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N']

    individuals = individual.Individual.from_list(fitnesses, names)
    actual = solve_instance.stochastic_uniform_sampling(
        individuals)
    expected = [
        individual.Individual(25, 'A'),
        individual.Individual(1, 'C'),
        individual.Individual(15, 'H'),
        individual.Individual(66, 'J'),
        individual.Individual(66, 'J'),
        individual.Individual(77, 'L'),
        individual.Individual(77, 'L'),
        individual.Individual(67, 'M'),
        individual.Individual(78, 'N'),
        individual.Individual(78, 'N'), ]
    assert actual == expected


def test_fps_windowed():
    solve_instance = solver.Solver('./config/test_config.json')
    solve_instance.windowed = True
    solve_instance.children = 5
    fitnesses = [10025, 10020, 10001, 10010, 10002, 10005, 10010,
                 10015, 10020, 10066, 10003, 10077, 10067, 10078]
    names = ['A', 'B', 'C', 'D', 'E', 'F',
             'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N']
    solve_instance.seed = 1
    solve_instance.set_seed()
    individuals = individual.Individual.from_list(fitnesses, names)
    actual = solve_instance.fitness_proportional_selection(
        individuals)
    expected = [individual.Individual(10010, 'D'),
                individual.Individual(10078, 'N'),
                individual.Individual(10067, 'M'),
                individual.Individual(10020, 'I'),
                individual.Individual(10077, 'L'),
                individual.Individual(10077, 'L'),
                individual.Individual(10067, 'M'),
                individual.Individual(10067, 'M'),
                individual.Individual(10020, 'B'),
                individual.Individual(10025, 'A')]

    assert actual == expected


def test_parent_tournament_selection():
    solve_instance = solver.Solver('./config/test_config.json')
    fitnesses = [25, 20, 1, 100, 2, 5, 10, 15, 20, 66, 3, 77, 67, 78]
    names = ['A', 'B', 'C', 'D', 'E', 'F',
             'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N']
    solve_instance.tournament_parent = 2
    solve_instance.children = 2
    solve_instance.seed = 15
    solve_instance.set_seed()
    individuals = individual.Individual.from_list(fitnesses, names)
    actual = solve_instance.tournament_selection_parent(
        individuals)
    expected = [individual.Individual(78, 'N'), individual.Individual(
        3, 'K'), individual.Individual(78, 'N'), individual.Individual(67, 'M')]

    assert actual == expected


def test_uniform_sampling():
    solve_instance = solver.Solver('./config/test_config.json')
    fitnesses = [25, 20, 1, 100, 2, 5, 10, 15, 20, 66, 3, 77, 67, 78]
    names = ['A', 'B', 'C', 'D', 'E', 'F',
             'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N']
    solve_instance.children = 2
    solve_instance.seed = 10
    solve_instance.set_seed()
    individuals = individual.Individual.from_list(fitnesses, names)
    actual = solve_instance.stochastic_uniform_sampling(
        individuals)
    expected = [
        individual.Individual(100, 'D'),
        individual.Individual(20, 'I'),
        individual.Individual(77, 'L'),
        individual.Individual(78, 'N')]
    assert actual == expected


def test_parent_tournament_survival():
    solve_instance = solver.Solver('./config/test_config.json')
    fitnesses = [25, 20, 1, 100, 2, 5, 10, 15, 20, 66, 3, 77, 67, 78]
    names = ['A', 'B', 'C', 'D', 'E', 'F',
             'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N']
    solve_instance.tournament_survival = 2
    solve_instance.parents = 2
    solve_instance.seed = 20
    solve_instance.set_seed()
    individuals = individual.Individual.from_list(fitnesses, names)

    actual = solve_instance.tournament_selection_survival(
        individuals)
    expected = [individual.Individual(77, 'L'), individual.Individual(
        78, 'N')]
    assert actual == expected


def test_truncation():
    solve_instance = solver.Solver('./config/test_config.json')
    solve_instance.parents = 2
    individuals = [individual.Individual(1, 'A'), individual.Individual(
        2, 'B'), individual.Individual(3, 'C'), individual.Individual(4, 'D')]

    actual = solve_instance.truncation(individuals)
    expected = [individual.Individual(4, 'D'), individual.Individual(3, 'C')]

    assert actual == expected


def test_num_of_evals_keep_going():
    solve_instance = solver.Solver('./config/test_config.json')
    actual = solve_instance.num_of_evals(10)
    expected = True
    assert actual == expected


def test_num_of_evals_done():
    solve_instance = solver.Solver('./config/test_config.json')
    actual = solve_instance.num_of_evals(30000)
    expected = False
    assert actual == expected


def test_no_change():
    solve_instance = solver.Solver('./config/test_config.json')
    solve_instance.n_termination = 4
    actual = solve_instance.no_change(3)
    expected = True
    assert actual == expected


def test_no_change_too_small():
    solve_instance = solver.Solver('./config/test_config.json')
    solve_instance.n_termination = 4
    actual = solve_instance.no_change(3)
    expected = True
    assert actual == expected


def test_no_change_no_change():
    solve_instance = solver.Solver('./config/test_config.json')
    solve_instance.n_termination = 4
    actual = solve_instance.no_change(4)
    expected = False
    assert actual == expected


def test_one_point_crossover():
    solve_instance = solver.Solver('./config/test_config.json')
    solve_instance.seed = 2
    solve_instance.set_seed()

    board = np.zeros([5, 5], dtype=int)
    board.fill(-1)
    board[1][2] = 2
    board[1][4] = 5
    board[2][1] = 0
    board[2][4] = 0
    board[3][3] = 5

    board = np.rot90(board)

    parent_one = individual.Individual(
        100, 'N', [[2, 0], [0, 4], [1, 1], [2, 3], [4, 1]], 5)
    parent_two = individual.Individual(
        60, 'L', [[2, 0], [0, 4], [1, 1], [2, 3]], 4)
    child = solve_instance.one_point_crossover(parent_one, parent_two)

    assert child == [[2, 0], [0, 4], [1, 1], [2, 3], [4, 1]]


def test_ea_run():
    solve_instance = solver.Solver('./config/test_config.json')

    solve_instance.run('./problems/a1.lup')


def test_uniform_random_constraint():
    # only one way to put in bulbs
    solve_instance = solver.Solver('./config/test_config.json')
    board = lightup.create_board('./problems/test.lup')
    solve_instance.shape = board.shape
    board = solve_instance.uniform_random_with_forced_validity(board)
    assert lightup.check_black_cell_constraint(board, False) == 0
