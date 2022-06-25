import random
import node
import solver
import gpac


def test_solver_init():
    instance = solver.Solver('config/test_run_config.json')
    assert instance.pill_density == 0.8
    assert instance.fruit_spawn_probability == 1
    assert instance.fruit_score == 100
    assert instance.time_multiplier == 10

    assert instance.max_runs == 1
    assert instance.max_evaluations == 2000

    assert instance.algorithm == "gp"

    assert instance.log_file == "./logs/test/test_run.log"
    assert instance.solution_file == "./solutions/test/test_solution.txt"
    assert instance.highest_score_file == "./worlds/test/test.txt"


def test_manhattan_distance():
    distance = solver.Solver._calculate_manhattan_distance([0, 0], [20, 20])
    assert distance == 40


def test_manhattan_distance_1():
    distance = solver.Solver._calculate_manhattan_distance([10, 0], [15, 20])
    assert distance == 25


def test_closest_ghost():
    instance = solver.Solver('config/test_run_config.json')
    instance.maps = ['maps/map0.txt']
    instance._create_game()

    closest_ghost_location = instance._closest_ghost([0, 0])
    assert closest_ghost_location == 53


def test_closest_pill():
    instance = solver.Solver('config/test_run_config.json')
    instance.seed = 10
    instance._set_seed()
    instance.maps = ['maps/map0.txt']
    instance._create_game()

    closest_pill_location = instance._closest_pill([0, 0])
    assert closest_pill_location == 1


def test_closest_pill_ontop():
    instance = solver.Solver('config/test_run_config.json')
    instance.seed = 10
    instance._set_seed()
    instance.maps = ['maps/map0.txt']
    instance._create_game()

    closest_pill_location = instance._closest_pill([0, 31])
    assert closest_pill_location == 0


def test_closest_fruit():
    instance = solver.Solver('config/test_run_config.json')
    instance.seed = 100
    instance._set_seed()
    instance.maps = ['maps/map0.txt']
    instance._create_game()

    closest_fruit_location = instance._closest_fruit([0, 0])
    assert closest_fruit_location == 36


def test_generate_pacman_weights():
    instance = solver.Solver('config/test_run_config.json')
    instance.seed = 100
    instance._set_seed()

    weights = instance._generate_pacman_weights()
    assert weights == [-0.7086614897917394, -0.0901459909719573,
                       0.5415676113180443, 0.4110264538680559]


def test_adjacent_walls():
    instance = solver.Solver('config/test_run_config.json')
    instance.maps = ['maps/map0.txt']
    instance._create_game()

    number_of_walls = instance._calculate_adjacent_walls([0, 0])
    assert number_of_walls == 0


def test_adjacent_walls_1():
    instance = solver.Solver('config/test_run_config.json')
    instance.maps = ['maps/map0.txt']
    instance._create_game()

    number_of_walls = instance._calculate_adjacent_walls([3, 2])
    assert number_of_walls == 2


def test_generate_sensor_inputs():
    instance = solver.Solver('config/test_run_config.json')
    instance.seed = 100
    instance._set_seed()
    instance.maps = ['maps/map0.txt']
    instance._create_game()

    sensor_inputs = instance._generate_sensor_inputs([0, 0])
    assert sensor_inputs == [53, 1, 0, 36]


# def test_calculate_move_scores():
#     instance = solver.Solver('config/test_run_config.json')
#     instance.seed = 100
#     instance._set_seed()
#     instance._create_game(['maps/map0.txt'])

#     weights = [-0.7086614897917394, -0.0901459909719573,
#                0.5415676113180443, 0.4110264538680559]

#     move_scores = instance._calculate_move_scores(weights)
#     assert move_scores == {'down': -23.184947846077847,
#                            'hold': -24.114296484291536, 'right': -23.184947846077847}


def test_select_best_move():
    move_scores = {'down': -30.603227393746806, 'hold': -
                   30.936206607853634, 'right': -30.603227393746806}
    assert solver.Solver._select_best_move(move_scores) == 'down'


# def test_random():
#     instance = solver.Solver('config/test_run_config.json')
#     instance.run(['maps/map0.txt'])


# def test_gp():
#     instance = solver.Solver('config/test_config.json')
#     instance._create_initial_population(['maps/map0.txt'])


def test_crossover():
    p1 = node.Node(data='*', depth=0)
    random.seed(3)
    p1.children[0] = node.Node(data='/', depth=1)
    p1.children[1] = node.Node(data='RAND', depth=1)
    p1.children[0].children[0] = node.Node(data=1.2, depth=2)
    p1.children[0].children[1] = node.Node(data='G', depth=2)
    p1.children[1].children[0] = node.Node(data='W', depth=2)
    p1.children[1].children[1] = node.Node(data='P', depth=2)
    p1.children[1].children[1].height = 0
    p1.children[1].children[0].height = 0
    p1.children[1].height = 1
    p1.children[0].height = 1
    p1.children[0].children[0].height = 0
    p1.children[0].children[1].height = 0
    p1.height = 2

    p2 = node.Node(data='-', depth=0)
    p2.children[0] = node.Node(data='+', depth=1)
    p2.children[1] = node.Node(data='RAND', depth=1)
    p2.children[0].children[0] = node.Node(data='F', depth=2)
    p2.children[0].children[1] = node.Node(data='P', depth=2)
    p2.children[1].children[0] = node.Node(data='W', depth=2)
    p2.children[1].children[1] = node.Node(data='F', depth=2)
    p2.children[1].children[1].height = 0
    p2.children[1].children[0].height = 0
    p2.children[1].height = 1
    p2.children[0].height = 1
    p2.children[0].children[0].height = 0
    p2.children[0].children[1].height = 0
    p2.height = 2

    child = solver.Solver.sub_tree_crossover(p1, p2)

    assert child.data == 'RAND'
    assert child.children[0].data == 'W'
    assert child.children[1].data == 'F'


def test_mutate():
    p1 = node.Node(data='*', depth=0)
    random.seed(1)
    p1.children[0] = node.Node(data='/', depth=1)
    p1.children[1] = node.Node(data='RAND', depth=1)
    p1.children[0].children[0] = node.Node(data=1.2, depth=2)
    p1.children[0].children[1] = node.Node(data='G', depth=2)
    p1.children[1].children[0] = node.Node(data='*', depth=2)
    p1.children[1].children[1] = node.Node(data='P', depth=2)
    p1.children[1].children[0].children[0] = node.Node(data=1, depth=3)
    p1.children[1].children[0].children[1] = node.Node(data=2, depth=3)

    p1.children[1].children[0].children[0].height = 0
    p1.children[1].children[0].children[1].height = 0
    p1.children[1].children[1].height = 1
    p1.children[1].children[0].height = 1
    p1.children[1].height = 2
    p1.children[0].height = 2
    p1.children[0].children[0].height = 1
    p1.children[0].children[1].height = 1
    p1.height = 3

    child = solver.Solver.sub_tree_mutation(p1)

    assert child.data == '*'
    assert child.children[0].data == '*'
    assert child.children[0].children[0].data == '/'
    assert child.children[0].children[0].children[0].data == 'W'
    assert child.children[0].children[0].children[1].data == 'W'
    assert child.children[0].children[1].data == 'G'
    assert child.children[1].data == 'RAND'
    assert child.children[1].children[0].data == '*'
    assert child.children[1].children[1].data == 'P'
    assert child.children[1].children[0].children[0].data == 1
    assert child.children[1].children[0].children[1].data == 2
