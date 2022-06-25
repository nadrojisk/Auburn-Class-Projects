import solver


def test_init():
    solve_instance = solver.Solver('./config/test_config.json')
    assert solve_instance.algorithm == "Random Search"
    assert solve_instance.seed is None
    assert solve_instance.num_of_runs == 10
    assert solve_instance.max_fitness == 1000
    assert solve_instance.log_file == "./logs/test_run.log"
    assert solve_instance.solution_file == "./solutions/test_solution.txt"
    assert solve_instance.evals == []
    assert solve_instance.ignore_black_cells == False


def test_run():
    solve_instance = solver.Solver('./config/test_config.json')
    solve_instance.run('./problems/a1.lup')


def test_big_run():
    solve_instance = solver.Solver('./config/config.json')
    solve_instance.run('./problems/a1.lup')
