from pathlib import Path
import os
import matplotlib.pyplot as plt
import re


def get_best_run(filename):
    eval_counts = []
    best_fitnesses = []
    avg_fitnesses = []
    with open(filename) as file:
        contents = file.read()
        best_eval = 0
        run_to_report = 0
        for _, run in enumerate(re.split('Run [0-9]*\n', contents)):
            if "Result Log" in run:
                continue
            best_eval_for_run = int(
                run.strip().split('\n')[-1].split('\t')[-1])

            if best_eval_for_run > best_eval:
                best_eval = best_eval_for_run

                run_to_report = run

    for line in run_to_report.strip().split('\n'):
        data = line.strip().split('\t')
        eval_point = data[0]
        avg_fitness = data[1]
        best_fitness = data[2]
        eval_counts.append(int(eval_point))
        best_fitnesses.append(float(best_fitness))
        avg_fitnesses.append(float(avg_fitness))
    return eval_counts, best_fitnesses, avg_fitnesses


def graph_compare(name, *filenames):
    evals = []
    best = []
    avg = []
    for filename in filenames:
        eval_cur, best_cur, avg_cur = get_best_run(filename)
        evals.append(eval_cur)
        best.append(best_cur)
        avg.append(avg_cur)

    plot_graph(name, filenames, "_best", [*evals], [*best], '')
    plot_graph(name, filenames, "_avg", [*evals], [*avg], '')


def plot_graph(name, filenames, suffix, evaluationes_list, fitnesses_list, title):
    for filename, evaluations, fitnesses in zip(filenames, evaluationes_list, fitnesses_list):
        plt.plot(evaluations, fitnesses, label=filename)

    plt.xlabel('Evaluation Count')
    plt.ylabel('Fitness')
    plt.title(title)
    plt.xlim(0, 2000)
    plt.ylim(0)
    plt.legend(loc="best")

    dirname = os.path.dirname(filenames[0]).split('/')[-1]

    Path(f'./doc/{dirname}').mkdir(parents=True, exist_ok=True)
    plt.savefig(f"./doc/{dirname}/{name}{suffix}.png")
    plt.show()
    plt.clf()


graph_compare('parsimony_total_nodes', 'logs/y1/config1_low.log',
              'logs/y1/config1_medium.log', 'logs/g2/config1.log')
graph_compare('parsimony_tree_height', 'logs/y1/config2_low.log',
              'logs/y1/config2_medium.log', 'logs/y1/config2_high.log')
graph_compare('parsimony_height_total', 'logs/y1/config1_medium.log', 'logs/y1/config1_low.log',
              'logs/g2/config1.log', 'logs/y1/config2_low.log', 'logs/y1/config2_medium.log',
              'logs/y1/config2_high.log')


graph_compare('config_compare', 'logs/g2/config1.log', 'logs/g2/config2.log', 'logs/g2/config3.log')
