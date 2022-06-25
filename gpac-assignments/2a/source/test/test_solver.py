import solver


def test_solver_init():
    instance = solver.Solver('config/test_config.json')
    assert instance.pill_density == 0.01
    assert instance.fruit_spawn_probability == 0.5
    assert instance.fruit_score == 100
    assert instance.time_multiplier == 10

    assert instance.max_runs == 30
    assert instance.max_evaluations == 10000

    assert instance.algorithm == "random"

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
    instance = solver.Solver('config/test_config.json')
    instance._create_game('maps/map0.txt')

    closest_ghost_location = instance._closest_ghost([0, 0])
    assert closest_ghost_location == 53


def test_closest_pill():
    instance = solver.Solver('config/test_config.json')
    instance.seed = 10
    instance._set_seed()
    instance._create_game('maps/map0.txt')

    closest_pill_location = instance._closest_pill([0, 0])
    assert closest_pill_location == 32


def test_closest_fruit():
    instance = solver.Solver('config/test_config.json')
    instance.seed = 100
    instance._set_seed()
    instance._create_game('maps/map0.txt')

    closest_fruit_location = instance._closest_fruit([0, 0])
    assert closest_fruit_location == 41


def test_create_game():
    instance = solver.Solver('config/test_config.json')
    instance.seed = 100
    instance._set_seed()
    instance._create_game('maps/map0.txt')

    assert instance.game_instance.locations['p'] == [[0, 34], [8, 16]]
    assert instance.game_instance.locations['f'] == [19, 22]


def test_generate_pacman_weights():
    instance = solver.Solver('config/test_config.json')
    instance.seed = 100
    instance._set_seed()

    weights = instance._generate_pacman_weights()
    assert weights == [-0.7086614897917394, -0.0901459909719573,
                       0.5415676113180443, 0.4110264538680559]


def test_adjacent_walls():
    instance = solver.Solver('config/test_config.json')
    instance._create_game('maps/map0.txt')

    number_of_walls = instance._calculate_adjacent_walls([0, 0])
    assert number_of_walls == 0


def test_adjacent_walls_1():
    instance = solver.Solver('config/test_config.json')
    instance._create_game('maps/map0.txt')

    number_of_walls = instance._calculate_adjacent_walls([3, 2])
    assert number_of_walls == 2


def test_generate_sensor_inputs():
    instance = solver.Solver('config/test_config.json')
    instance.seed = 100
    instance._set_seed()
    instance._create_game('maps/map0.txt')

    sensor_inputs = instance._generate_sensor_inputs([0, 0])
    assert sensor_inputs == [53, 24, 0, 41]


def test_calculate_move_scores():
    instance = solver.Solver('config/test_config.json')
    instance.seed = 100
    instance._set_seed()
    instance._create_game('maps/map0.txt')

    weights = [-0.7086614897917394, -0.0901459909719573,
               0.5415676113180443, 0.4110264538680559]

    move_scores = instance._calculate_move_scores(weights)
    assert move_scores == {'down': -21.941129495485185,
                           'hold': -22.87047813369887, 'right': -21.941129495485185}


def test_select_best_move():
    move_scores = {'down': -30.603227393746806, 'hold': -
                   30.936206607853634, 'right': -30.603227393746806}
    assert solver.Solver._select_best_move(move_scores) == 'down'


# def test_random():
#     instance = solver.Solver('config/test_config.json')
#     instance.run('maps/map0.txt')
