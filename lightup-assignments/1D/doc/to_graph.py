from os import walk
import os
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import re


def to_graph(filename):

    with open(filename) as file:
        contents = None
        for line in file:
            if 'Run' in line:
                contents = file.read()
                break
        if not contents:
            return
        runs = {}
        for run in re.split('Run [0-9]*\n', contents):

            for generation in run.strip().split('\n'):
                if not generation or "Runtime" in generation:
                    continue
                eval_for_gen, avg_lit_for_gen, max_lit_for_gen, avg_black_cell_for_gen, min_black_cell_for_gen, avg_bulb_for_gen, min_bulb_for_gen, crowding = generation.strip().split(
                    '\t')
                eval_for_gen = int(eval_for_gen)
                if runs.get(eval_for_gen) is None:
                    runs[eval_for_gen] = {}
                    runs[eval_for_gen]['avg_lit'] = []
                    runs[eval_for_gen]['lit_list'] = []
                    runs[eval_for_gen]['avg_black'] = []
                    runs[eval_for_gen]['black_list'] = []
                    runs[eval_for_gen]['avg_bulb'] = []
                    runs[eval_for_gen]['bulb_list'] = []
                    runs[eval_for_gen]['crowding'] = []

                eval_dict = runs[eval_for_gen]

                eval_dict['avg_lit'].append(float(avg_lit_for_gen))
                eval_dict['lit_list'].append(int(max_lit_for_gen))
                eval_dict['avg_black'].append(float(avg_black_cell_for_gen))
                eval_dict['black_list'].append(int(min_black_cell_for_gen))
                eval_dict['avg_bulb'].append(float(avg_bulb_for_gen))
                eval_dict['bulb_list'].append(int(min_bulb_for_gen))
                eval_dict['crowding'].append(float(min_bulb_for_gen))

    # avg everything
    average_average_lit = []
    average_best_lit = []

    average_average_black = []
    average_best_black = []

    average_average_bulb = []
    average_best_bulb = []

    for _, values in runs.items():
        avg_avg_lit = round(sum(values['avg_lit']) / len(values['avg_lit']), 2)
        avg_lit = round(
            sum(values['lit_list']) / len(values['lit_list']), 2)

        average_average_lit.append(avg_avg_lit)
        average_best_lit.append(avg_lit)

        avg_avg_black = round(
            sum(values['avg_black']) / len(values['avg_black']), 2)
        avg_black = round(
            sum(values['black_list']) / len(values['black_list']), 2)

        average_average_black.append(avg_avg_black)
        average_best_black.append(avg_black)

        avg_avg_bulb = round(
            sum(values['avg_bulb']) / len(values['avg_bulb']), 2)
        avg_bulb = round(
            sum(values['bulb_list']) / len(values['bulb_list']), 2)

        average_average_bulb.append(avg_avg_bulb)
        average_best_bulb.append(avg_bulb)

    plt.figure()

    plt.plot(list(runs.keys()), average_average_lit, 'b')
    plt.plot(list(runs.keys()), average_best_lit, 'b:')

    plt.plot(list(runs.keys()), average_average_black, 'r')
    plt.plot(list(runs.keys()), average_best_black, 'r:')

    plt.plot(list(runs.keys()), average_average_bulb, 'g')
    plt.plot(list(runs.keys()), average_best_bulb, 'g:')

    plt.xlabel('Evaluations')
    plt.ylabel('Sub-Objectives')
    plt.title(filename.split('/')[-1])
    plt.xlim(0, 10000)
    plt.ylim(0, 100)
    red_patch = mpatches.Patch(
        color='red', label='Average Black Cell Violation', lw=1)
    red_dot_patch = mpatches.Patch(
        color='red', label='Best Black Cell Violation', ls=':', lw=1)

    blue_patch = mpatches.Patch(color='blue', label='Average Percentage Lit')
    blue_dot_patch = mpatches.Patch(
        color='blue', label='Best Percentage Lit', ls=':')

    green_patch = mpatches.Patch(color='green', label='Average Bulb Violation')
    green_dot_patch = mpatches.Patch(
        color='green', label='Best Bulb Violation', ls=':')

    plt.legend(handles=[red_patch, red_dot_patch,
                        blue_patch, blue_dot_patch, green_patch, green_dot_patch], loc='best')
    savefile = filename.split('/')[-1][:-4]
    plt.savefig(f"./doc/problem_{savefile}.png")
    plt.show()


for (dirpath, dirnames, filenames) in walk('./logs/'):
    for filename in filenames:
        if ('.log' in filename):
            to_graph(os.path.join(dirpath, filename))
