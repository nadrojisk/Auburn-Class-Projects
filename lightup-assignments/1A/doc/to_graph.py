import matplotlib.pyplot as plt
import re


def to_graph(filename):
    eval_counts = []
    fitnesses = []
    with open(filename) as file:
        contents = file.read()
        best_eval = 0
        run_to_report = 0
        for count, run in enumerate(re.split('Run [0-9]*\n', contents)):
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
    plt.plot(fitnesses, eval_counts, 'b^-')
    plt.xlabel('fitness')
    plt.ylabel('eval')
    plt.title('evals versus fitness plot')
    savefile = filename.split('_')[0].split('/')[-1]
    plt.savefig(f"./doc/problem_{savefile}.png")
    plt.show()


to_graph('./logs/1_run.log')
to_graph('./logs/2_run.log')
to_graph('./logs/3_run.log')
