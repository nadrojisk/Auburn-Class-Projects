import os
import matplotlib.pyplot as plt
import re

from matplotlib.pyplot import plot


def graph_best_run(filename):
    eval_counts = []
    fitnesses = []
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
                if best_eval == 100:
                    break

    for line in run_to_report.strip().split('\n'):
        data = line.strip().split('\t')
        eval_point = data[0]
        fitness = data[1]
        eval_counts.append(int(eval_point))
        fitnesses.append(int(fitness))

    plot_graph(filename, "_best_run", [eval_counts], [fitnesses], 'Best Run')


def graph_all_runs(filename):

    evaluation_counts_over_runs = []
    fitnesses_over_runs = []
    with open(filename, "r") as file:
        contents = file.read()

    for _, run in enumerate(re.split('Run [0-9]*\n', contents)):
        if "Result Log" in run:
            continue
        evals = run.strip().split('\n')

        fitnesses = []
        evaluations = []
        for eval in evals:
            eval_count, fitness = [int(instance) for instance in eval.split('\t')]
            fitnesses.append(fitness)
            evaluations.append(eval_count)

        evaluation_counts_over_runs.append(evaluations)
        fitnesses_over_runs.append(fitnesses)

    plot_graph(filename, "_all_runs", evaluation_counts_over_runs, fitnesses_over_runs, 'All Runs')


def plot_graph(filename, suffix, evaluationes_list, fitnesses_list, title):
    for evaluations, fitnesses in zip(evaluationes_list, fitnesses_list):
        plt.plot(fitnesses, evaluations)

    plt.xlabel('Fitness')
    plt.ylabel('Evaluation Count')
    plt.title(title)
    plt.ylim(0, 2000)

    savefile = os.path.splitext(os.path.basename(filename))[0]

    plt.savefig(f"./doc/{savefile}{suffix}.png")
    plt.show()
    plt.clf()


def graph(filename):
    graph_all_runs(filename)
    graph_best_run(filename)


graph('./logs/g1/config1.log')
graph('./logs/g1/config2.log')
graph('./logs/g1/config3.log')
