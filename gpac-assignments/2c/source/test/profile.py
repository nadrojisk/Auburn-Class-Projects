""" Module for just a test driver """
import solver

instance = solver.Solver('config/g2_default.json', True)
instance.seed = 1604690777
# try:
instance.run()
# except:
#     print(instance.seed)
