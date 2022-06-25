import solver

instance = solver.Solver('config/test_run_config.json', True)
instance.seed = 1604690777
# try:
instance.run()
# except:
#     print(instance.seed)
