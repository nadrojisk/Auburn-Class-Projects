import individual
import solver
import numpy as np


def test_init():
    solve_instance = solver.Solver('./config/test/test_config.json')
    assert solve_instance.seed is None
    assert solve_instance.num_of_runs == 30
    assert solve_instance.max_evals == 10000
    assert solve_instance.log_file == "./logs/bc1_test_run.log"
    assert solve_instance.solution_file == "./solutions/bc1_test_solution.txt"
    assert solve_instance.parent_selection_alg == "sus"
    assert solve_instance.recombination_alg == "one point crossover"
    assert solve_instance.survival_selection_alg == "truncation"
    assert solve_instance.termination_alg == "num of evals"
    assert solve_instance.initialization_alg == "vanilla"
    assert solve_instance.survival_strategy_alg == "plus"
    assert solve_instance.mutation_rate == .40
    assert solve_instance.ignore_black_cells


def test_uniform_random_parent():
    solve_instance = solver.Solver('./config/test/test_config.json')

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


def test_uniform_random_survival():
    solve_instance = solver.Solver('./config/test/test_config.json')

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
    solve_instance = solver.Solver('./config/test/test_config.json')

    solve_instance.children = 5
    solve_instance.seed = 1
    solve_instance.set_seed()
    fitnesses = [25, 20, 1, 10, 2, 5, 10, 15, 20, 66, 3, 77, 67, 78]
    names = ['A', 'B', 'C', 'D', 'E', 'F',
             'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N']

    individuals = individual.Individual.from_list(fitnesses, names)
    actual = solve_instance.fitness_proportional_selection(
        individuals)
    expected = [individual.Individual(fitness=10, name='D'),
                individual.Individual(fitness=78, name='N'),
                individual.Individual(fitness=67, name='M'),
                individual.Individual(fitness=20, name='I'),
                individual.Individual(fitness=77, name='L'),
                individual.Individual(fitness=77, name='L'),
                individual.Individual(fitness=67, name='M'),
                individual.Individual(fitness=67, name='M'),
                individual.Individual(fitness=20, name='B'),
                individual.Individual(fitness=25, name='A')]
    assert actual == expected


def test_fps_survival():
    solve_instance = solver.Solver('./config/test/test_config.json')

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
    solve_instance = solver.Solver('./config/test/test_config.json')
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
        individual.Individual(fitness=25, name='A'),
        individual.Individual(fitness=1, name='C'),
        individual.Individual(fitness=15, name='H'),
        individual.Individual(fitness=66, name='J'),
        individual.Individual(fitness=66, name='J'),
        individual.Individual(fitness=77, name='L'),
        individual.Individual(fitness=77, name='L'),
        individual.Individual(fitness=67, name='M'),
        individual.Individual(fitness=78, name='N'),
        individual.Individual(fitness=78, name='N'), ]
    assert actual == expected


def test_parent_tournament_selection():
    solve_instance = solver.Solver('./config/test/test_config.json')
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
    expected = [
        individual.Individual(fitness=78, name='N'),
        individual.Individual(fitness=3, name='K'),
        individual.Individual(fitness=78, name='N'),
        individual.Individual(fitness=67, name='M')]

    assert actual == expected


def test_uniform_sampling():
    solve_instance = solver.Solver('./config/test/test_config.json')
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
        individual.Individual(fitness=100, name='D'),
        individual.Individual(fitness=20, name='I'),
        individual.Individual(fitness=77, name='L'),
        individual.Individual(fitness=78, name='N')]
    assert actual == expected


def test_parent_tournament_survival():
    solve_instance = solver.Solver('./config/test/test_config.json')
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
    expected = [
        individual.Individual(fitness=77, name='L'),
        individual.Individual(fitness=78, name='N')]
    assert actual == expected


def test_truncation():
    solve_instance = solver.Solver('./config/test/test_config.json')
    solve_instance.parents = 2
    individuals = [individual.Individual(1, 'A'), individual.Individual(
        2, 'B'), individual.Individual(3, 'C'), individual.Individual(4, 'D')]

    actual = solve_instance.truncation(individuals)
    expected = [individual.Individual(4, 'D'), individual.Individual(3, 'C')]

    assert actual == expected


def test_num_of_evals_keep_going():
    solve_instance = solver.Solver('./config/test/test_config.json')
    actual = solve_instance.num_of_evals(10)
    expected = True
    assert actual == expected


def test_num_of_evals_done():
    solve_instance = solver.Solver('./config/test/test_config.json')
    actual = solve_instance.num_of_evals(30000)
    expected = False
    assert actual == expected


def test_no_change():
    solve_instance = solver.Solver('./config/test/test_config.json')
    solve_instance.n_termination = 4
    actual = solve_instance.no_change(3)
    expected = True
    assert actual == expected


def test_no_change_too_small():
    solve_instance = solver.Solver('./config/test/test_config.json')
    solve_instance.n_termination = 4
    actual = solve_instance.no_change(3)
    expected = True
    assert actual == expected


def test_no_change_no_change():
    solve_instance = solver.Solver('./config/test/test_config.json')
    solve_instance.n_termination = 4
    actual = solve_instance.no_change(4)
    expected = False
    assert actual == expected


def test_one_point_crossover():
    solve_instance = solver.Solver('./config/test/test_config.json')
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
        100, 'N', [[2, 0], [0, 4], [1, 1], [2, 3], [4, 1]])
    parent_two = individual.Individual(
        60, 'L', [[2, 0], [0, 4], [1, 1], [2, 3]])
    child = solve_instance.one_point_crossover(parent_one, parent_two)

    assert child == [[2, 0], [0, 4], [1, 1], [2, 3], [4, 1]]


# def test_ea_run():
#     solve_instance = solver.Solver('./config/d1_test.json')
#     solve_instance.diversity_algorithm = 'sharing'
#     solve_instance.sigma = 15
#     solve_instance.run('./problems/d1.lup')


def test_survival_strat_comma():
    solve_instance = solver.Solver('./config/test/test_config.json')
    solve_instance.survival_strategy_alg = 'comma'

    fitnesses = [25, 20, 1, 100, 2, 5]
    existing_names = ['A', 'B', 'C', 'D', 'E', 'F']

    child_names = ['0', '1', '2', '3', '4', '5', '6']

    existing = individual.Individual.from_list(fitnesses, existing_names)
    children = individual.Individual.from_list(fitnesses, child_names)

    assert solve_instance.survival_strategy_selection(
        existing, children) == children


def test_survival_strat_plus():
    solve_instance = solver.Solver('./config/test/test_config.json')
    solve_instance.survival_strategy_alg = 'plus'

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


def test_dom_sort():
    a_ind = individual.Individual(
        90, black_cell_violations=1, bulb_violations=1)
    b_ind = individual.Individual(
        90, black_cell_violations=0, bulb_violations=0)
    c_ind = individual.Individual(
        100, black_cell_violations=0, bulb_violations=0)
    d_ind = individual.Individual(
        90, black_cell_violations=0, bulb_violations=0)
    instance = solver.Solver('./config/test/test_config.json')

    instance.diversity_algorithm = 'vanilla'
    instance.calculate_moea_fitness([d_ind, c_ind, b_ind, a_ind])

    assert a_ind.fitness == 98
    assert d_ind.fitness == 99
    assert c_ind.fitness == 100
    assert b_ind.fitness == 99


def test_dom_2():
    ind_1 = individual.Individual(
        8, name='1', black_cell_violations=(10 - 2), bulb_violations=0)
    ind_2 = individual.Individual(
        4, name='2', black_cell_violations=(10 - 1), bulb_violations=0)
    ind_3 = individual.Individual(
        2, name='3', black_cell_violations=(10 - 3), bulb_violations=0)
    ind_4 = individual.Individual(
        1, name='4', black_cell_violations=(10 - 2), bulb_violations=0)
    ind_5 = individual.Individual(
        9, name='5', black_cell_violations=(10 - 1), bulb_violations=0)
    ind_6 = individual.Individual(
        4, name='6', black_cell_violations=(10 - 7), bulb_violations=0)
    ind_7 = individual.Individual(
        2, name='7', black_cell_violations=(10 - 5), bulb_violations=0)
    ind_8 = individual.Individual(
        1, name='8', black_cell_violations=(10 - 3), bulb_violations=0)
    ind_9 = individual.Individual(
        10, name='9', black_cell_violations=(10 - 7), bulb_violations=0)
    ind_10 = individual.Individual(
        5, name='10', black_cell_violations=(10 - 5), bulb_violations=0)

    instance = solver.Solver('./config/test/test_config.json')

    instance.diversity_algorithm = 'vanilla'
    instance.calculate_moea_fitness(
        [ind_1, ind_2, ind_3, ind_4, ind_5, ind_6, ind_7, ind_8, ind_9, ind_10])

    assert ind_9.fitness == 100

    assert ind_1.fitness == 99
    assert ind_5.fitness == 99
    assert ind_6.fitness == 99
    assert ind_10.fitness == 99
    assert ind_2.fitness == 98
    assert ind_7.fitness == 98
    assert ind_3.fitness == 97
    assert ind_8.fitness == 96
    assert ind_4.fitness == 95


def test_fitness_sharing():
    ind_1 = individual.Individual(
        80, name='1', black_cell_violations=(10 - 2), bulb_violations=0)
    ind_2 = individual.Individual(
        40, name='2', black_cell_violations=(10 - 1), bulb_violations=0)
    ind_3 = individual.Individual(
        20, name='3', black_cell_violations=(10 - 3), bulb_violations=0)
    ind_4 = individual.Individual(
        10, name='4', black_cell_violations=(10 - 2), bulb_violations=0)
    ind_5 = individual.Individual(
        90, name='5', black_cell_violations=(10 - 1), bulb_violations=0)
    ind_6 = individual.Individual(
        40, name='6', black_cell_violations=(10 - 7), bulb_violations=0)
    ind_7 = individual.Individual(
        20, name='7', black_cell_violations=(10 - 5), bulb_violations=0)
    ind_8 = individual.Individual(
        10, name='8', black_cell_violations=(10 - 3), bulb_violations=0)
    ind_9 = individual.Individual(
        100, name='9', black_cell_violations=(10 - 7), bulb_violations=0)
    ind_10 = individual.Individual(
        50, name='10', black_cell_violations=(10 - 5), bulb_violations=0)

    individuals = [ind_1, ind_2, ind_3, ind_4,
                   ind_5, ind_6, ind_7, ind_8, ind_9, ind_10]
    instance = solver.Solver('./config/test/test_config.json')
    instance.sigma = 15
    instance.diversity_algorithm = 'sharing'
    _ = instance.calculate_moea_fitness(individuals)

    assert round(ind_1.fitness, 2) == 99.38
    assert round(ind_2.fitness, 2) == 98.27
    assert round(ind_3.fitness, 2) == 97.20
    assert round(ind_4.fitness, 2) == 95.19
    assert round(ind_5.fitness, 2) == 99.32
    assert round(ind_6.fitness, 2) == 99.26
    assert round(ind_7.fitness, 2) == 98.20
    assert round(ind_8.fitness, 2) == 96.19
    assert round(ind_9.fitness, 2) == 100.41
    assert round(ind_10.fitness, 2) == 99.31


def test_crowding():
    ind_1 = individual.Individual(
        80, name='1', black_cell_violations=(8), bulb_violations=1)
    ind_2 = individual.Individual(
        40, name='2', black_cell_violations=(9), bulb_violations=2)
    ind_3 = individual.Individual(
        20, name='3', black_cell_violations=(7), bulb_violations=3)
    ind_4 = individual.Individual(
        10, name='4', black_cell_violations=(8), bulb_violations=5)
    ind_5 = individual.Individual(
        90, name='5', black_cell_violations=(9), bulb_violations=0)
    ind_6 = individual.Individual(
        40, name='6', black_cell_violations=(3), bulb_violations=2)
    ind_7 = individual.Individual(
        20, name='7', black_cell_violations=(5), bulb_violations=2)
    ind_8 = individual.Individual(
        10, name='8', black_cell_violations=(7), bulb_violations=3)
    ind_9 = individual.Individual(
        100, name='9', black_cell_violations=(3), bulb_violations=0)
    ind_10 = individual.Individual(
        50, name='10', black_cell_violations=(5), bulb_violations=1)

    individuals = [ind_1, ind_2, ind_3, ind_4,
                   ind_5, ind_6, ind_7, ind_8, ind_9, ind_10]
    instance = solver.Solver('./config/test/test_config.json')
    instance.sigma = 15
    instance.diversity_algorithm = 'crowding'
    _ = instance.calculate_moea_fitness(individuals)
    assert ind_1.fitness == 99.5
    assert round(ind_2.fitness, 2) == 98.99
    assert round(ind_3.fitness, 2) == 97.99
    assert round(ind_4.fitness, 2) == 95.99
    assert round(ind_5.fitness, 2) == 99.99
    assert round(ind_6.fitness, 2) == 99.99
    assert round(ind_7.fitness, 2) == 98.99
    assert round(ind_8.fitness, 2) == 96.99
    assert round(ind_9.fitness, 2) == 100.99
