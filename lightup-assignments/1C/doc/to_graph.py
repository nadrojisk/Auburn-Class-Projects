import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import re


def to_graph(filename):

    with open(filename) as file:
        for line in file:
            if 'Run' in line:
                contents = file.read()
                break

        runs = {}
        for run in re.split('Run [0-9]*\n', contents):

            for generation in run.strip().split('\n'):

                eval_for_gen, avg_fit_for_gen, max_fit_for_gen = generation.strip().split(
                    '\t')
                eval_for_gen = int(eval_for_gen)
                if runs.get(eval_for_gen) is None:
                    runs[eval_for_gen] = {}
                    runs[eval_for_gen]['avg_list'] = []
                    runs[eval_for_gen]['fitness_list'] = []

                eval_dict = runs[eval_for_gen]

                eval_dict['avg_list'].append(float(avg_fit_for_gen))
                eval_dict['fitness_list'].append(int(max_fit_for_gen))

    # avg everything
    average_average_fitnesses = []
    average_best_fitness = []

    for _, values in runs.items():
        avg_avg = round(sum(values['avg_list']) / len(values['avg_list']), 2)
        avg_fitness = round(
            sum(values['fitness_list']) / len(values['fitness_list']), 2)

        average_average_fitnesses.append(avg_avg)
        average_best_fitness.append(avg_fitness)

    plt.figure()

    plt.plot(list(runs.keys()), average_average_fitnesses, 'b')

    plt.plot(list(runs.keys()), average_best_fitness, 'r')
    plt.xlabel('Evaluations')
    plt.ylabel('Fitness')
    plt.xlim(0, 10000)
    plt.ylim(0, 100)
    red_patch = mpatches.Patch(color='red', label='Best')
    blue_patch = mpatches.Patch(color='blue', label='Average')
    plt.legend(handles=[red_patch, blue_patch], loc='lower right')
    savefile = filename.split('/')[-1][:-4]
    plt.savefig(f"./doc/problem_{savefile}.png")
    plt.show()


to_graph('./logs/bc1/bc1_run.log')
to_graph('./logs/bc2/bc2_run.log')
to_graph('./logs/c1/c1_run.log')
to_graph('./logs/c2/c2_run.log')
