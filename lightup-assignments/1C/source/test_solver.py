import individual
import solver as solver
import lightup
import numpy as np


def test_init():
    solve_instance = solver.Solver('./config/test_config.json')
    assert solve_instance.seed is None
    assert solve_instance.num_of_runs == 30
    assert solve_instance.fitness_evals == 10000
    assert solve_instance.log_file == "./logs/bc1_test_run.log"
    assert solve_instance.solution_file == "./solutions/bc1_test_solution.txt"
    assert solve_instance.parent_algorithm == "sus"
    assert solve_instance.child_algorithm == "one point crossover"
    assert solve_instance.survival_algorithm == "truncation"
    assert solve_instance.termination_algorithm == "num of evals"
    assert solve_instance.initialization_algorithm == "vanilla"
    assert solve_instance.survival_strategy_algorithm == "plus"
    assert solve_instance.mutation_rate == .40
    assert solve_instance.penalty_coefficient == 10
    assert solve_instance.constraint_algorithm == "penalty"
    assert solve_instance.ignore_black_cells == True


def test_uniform_random_parent():
    solve_instance = solver.Solver('./config/test_config.json')

    solve_instance.children = 2
    solve_instance.seed = 1
    solve_instance.set_seed()

    fitnesses = [25, 20, 1, 10, 2, 5, 10, 15, 20, 66, 3, 77, 67, 78]
    names = ['A', 'B', 'C', 'D', 'E', 'F',
             'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N']

    individuals = individual.Individual.from_list(fitnesses, names)

    expected = individual.Individual.from_list(
        [20, 77, 3, 10], ['B', 'L', 'K', 'D'])
    actual = solve_instance.uniform_random_parent(individuals)

    assert actual == expected


def test_penalty_function():
    solve_instance = solver.Solver('./config/test_config.json')
    intersections = {'[ 10 100  10 100 100]': [1],
                     '[ 10 10 10 100 100]': [2]}
    black_cells = {4: [1], 0: [3]}

    actual = solve_instance.penalty_function(
        100, black_cells, intersections, 10)
    expected = 10
    assert actual == expected


def test_uniform_random_survival():
    solve_instance = solver.Solver('./config/test_config.json')

    solve_instance.parents = 4
    solve_instance.seed = 100
    solve_instance.set_seed()

    fitnesses = [25, 20, 1, 10, 2, 5, 10, 15, 20, 66, 3, 77, 67, 78]
    names = ['A', 'B', 'C', 'D', 'E', 'F',
             'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N']

    individuals = individual.Individual.from_list(fitnesses, names)

    expected = individual.Individual.from_list(
        [1, 15, 67, 78], ['C', 'H', 'M', 'N'])
    actual = solve_instance.uniform_random_survival(individuals)

    assert actual == expected


def test_fps():
    solve_instance = solver.Solver('./config/test_config.json')

    solve_instance.children = 5
    solve_instance.seed = 1
    solve_instance.set_seed()
    fitnesses = [25, 20, 1, 10, 2, 5, 10, 15, 20, 66, 3, 77, 67, 78]
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


def test_fps_survival():
    solve_instance = solver.Solver('./config/test_config.json')

    solve_instance.children = 2
    solve_instance.seed = 10
    solve_instance.set_seed()
    fitnesses = [25, 20, 1, 10, 2, 5, 10, 15, 20, 66, 3, 77, 67, 78]
    names = ['A', 'B', 'C', 'D', 'E', 'F',
             'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N']

    individuals = individual.Individual.from_list(fitnesses, names)
    actual = solve_instance.fitness_proportional_selection_survival(
        individuals)
    expected = individual.Individual.from_list(
        [67, 25, 77, 66], ['M', 'A', 'L', 'J'])
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


def test_calculate_fitness_with_penalty():
    solve_instance = solver.Solver('./config/bc1_config.json')

    board = np.array([[10, 100,  10,   1,  10,  10],
                      [0,  10,  10,  10,   5,  10],
                      [10,  10,  10,  10,   1,  10],
                      [5,  10,  10,  10,  10,  10],
                      [10,  10,  10,  10,  10,  10],
                      [100,  10,  10,  10,   2,   5]])
    fitness, penalty = solve_instance.calculate_fitness(board, 10)
    assert fitness == -280
    assert penalty == 380


# def test_ea_run():
#     solve_instance = solver.Solver('./config/c1_config_adap_pen.json')

#     solve_instance.run('./problems/c1.lup')


def test_uniform_random_constraint():
    # only one way to put in bulbs
    solve_instance = solver.Solver('./config/test_config.json')
    board = lightup.create_board('./problems/test.lup')
    solve_instance.shape = board.shape
    board = solve_instance.uniform_random_with_forced_validity(board)
    assert lightup.check_black_cells(board, False) == {}


def test_survival_strat_comma():
    solve_instance = solver.Solver('./config/test_config.json')
    solve_instance.survival_strategy_algorithm = 'comma'

    fitnesses = [25, 20, 1, 100, 2, 5]
    existing_names = ['A', 'B', 'C', 'D', 'E', 'F']

    child_names = ['0', '1', '2', '3', '4', '5', '6']

    existing = individual.Individual.from_list(fitnesses, existing_names)
    children = individual.Individual.from_list(fitnesses, child_names)

    assert solve_instance.survival_strategy_selection(
        existing, children) == children


def test_survival_strat_plus():
    solve_instance = solver.Solver('./config/test_config.json')
    solve_instance.survival_strategy_algorithm = 'plus'

    fitnesses = [25, 20, 1, 100, 2, 5]
    existing_names = ['A', 'B', 'C', 'D', 'E', 'F']

    child_names = ['0', '1', '2', '3', '4', '5', '6']

    existing = individual.Individual.from_list(fitnesses, existing_names)
    children = individual.Individual.from_list(fitnesses, child_names)

    expected = list(existing)
    expected.extend(children)
    actual = solve_instance.survival_strategy_selection(
        existing, children)
    assert actual == expected
