import solver
instance = solver.Solver('config/test_config_2.json', True)
instance.seed = 1
instance.run('maps/map0.txt')
