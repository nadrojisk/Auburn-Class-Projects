import multiprocessing
import tqdm
import solver

configs = ['config/g1_1.json', 'config/g1_2.json', 'config/g1_3.json']


def run(config):
    solver.Solver(config, False).run('maps/map0.txt')


with multiprocessing.Pool() as pool:
    r = list(tqdm.tqdm(pool.imap(run, configs), total=len(configs)))
