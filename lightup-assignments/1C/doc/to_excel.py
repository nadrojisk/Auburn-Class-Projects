import glob
import xlsxwriter


def get_contents(filename, problem):
    with open(f'./logs/{problem}/{filename}') as file:
        data = file.read().strip().split('\n')
    data = [float(cell) for cell in data]
    return data


def main():

    problems = glob.glob('./problems/bc*')

    for file in sorted(problems):

        problem = file.split('/')[-1].split('.')[0]
        workbook = xlsxwriter.Workbook(f'./doc/green3_{problem}.xlsx')

        # Vanilla v Penalty Constraint
        worksheet = workbook.add_worksheet("Green 3.1")
        cur_row = 0
        col1 = problem + "_run_best_from_gen_1b.log"
        col2 = problem + "_run_best_from_gen.log"
        cur_row = dump_two_log(problem,
                               'Vanilla EA', 'Penalty Constrain EA', col1, col2, worksheet, cur_row)

        # Vanilla Validity v Penalty Validity
        worksheet = workbook.add_worksheet("Green 3.2 1B-1C")
        cur_row = 0
        col1 = problem + "_validity_run_best_from_gen_1b.log"
        col2 = problem + "_validity_run_best_from_gen.log"

        cur_row = dump_two_log(problem,
                               'Vanilla Validity EA', 'Penalty Validity Ea', col1, col2, worksheet, cur_row)

        # Vanilla v Vanilla Validity
        worksheet = workbook.add_worksheet("Green 3.2 1B-1B")
        cur_row = 0
        col1 = problem + "_run_best_from_gen_1b.log"
        col2 = problem + "_validity_run_best_from_gen_1b.log"
        cur_row = dump_two_log(problem,
                               'Vanilla EA', 'Vanilla Validity EA', col1, col2, worksheet, cur_row)

        workbook.close()

    problems = glob.glob('./problems/c*')
    for file in sorted(problems):
        problem = file.split('/')[-1].split('.')[0]
        workbook = xlsxwriter.Workbook(f'./doc/green3_{problem}.xlsx')

        # Vanilla Validity v Penalty Validity
        worksheet = workbook.add_worksheet("Green 3.2")
        cur_row = 0
        col1 = problem + "_run_best_from_gen.log"
        col2 = problem + "_validity_run_best_from_gen.log"

        cur_row = dump_two_log(problem,
                               'Vanilla Penalty EA', 'Penalty Validity Ea', col1, col2, worksheet, cur_row)

        # 5 Penalty Coef v 10 Penalty Coef
        worksheet = workbook.add_worksheet("Green 3.3 5-10")
        cur_row = 0
        col1 = problem + "_run_best_from_gen.log"
        col2 = problem + "_validity_5_run_best_from_gen.log"

        cur_row = dump_two_log(problem,
                               '10 Coef', '5 Coef', col1, col2, worksheet, cur_row)

        # 50 Penalty Coef v 10 Penalty Coef
        worksheet = workbook.add_worksheet("Green 3.3 50-10")
        cur_row = 0
        col1 = problem + "_run_best_from_gen.log"
        col2 = problem + "_validity_50_run_best_from_gen.log"

        cur_row = dump_two_log(problem,
                               '10 Coef', '50 Coef', col1, col2, worksheet, cur_row)

        # 50 Penalty Coef v 5 Penalty Coef
        worksheet = workbook.add_worksheet("Green 3.3 50-5")
        cur_row = 0
        col1 = problem + "_validity_5_run_best_from_gen.log"
        col2 = problem + "_validity_50_run_best_from_gen.log"

        cur_row = dump_two_log(problem,
                               '5 Coef', '50 Coef', col1, col2, worksheet, cur_row)

        # Validity Forced v Adaptive Mutation Validity Forced
        worksheet = workbook.add_worksheet("Yellow 1")
        cur_row = 0
        col1 = problem + "_validity_run_best_from_gen.log"
        col2 = problem + "_self_mut_run_best_from_gen.log"

        cur_row = dump_two_log(problem,
                               'Base', 'self-adaptivity mutation', col1, col2, worksheet, cur_row)

        # Validity Forced v Adaptive Penalty Validity Forced
        worksheet = workbook.add_worksheet("Red 2")
        cur_row = 0
        col1 = problem + "_validity_run_best_from_gen.log"
        col2 = problem + "_self_pen_run_best_from_gen.log"

        cur_row = dump_two_log(problem,
                               'Base', 'self-adaptivity penalty', col1, col2, worksheet, cur_row)

        workbook.close()


def dump_two_log(problem, column1_header, column2_header, column1, column2, worksheet, row, col=0, ):

    column1_data = get_contents(column1, problem)
    column2_data = get_contents(column2, problem)

    cur_row = write_data(worksheet, column1_header, column2_header,
                         column1_data, column2_data, row, col)
    return cur_row


def write_data(worksheet, column1_header, column2_header, column1_data, column2_data, row, col):

    worksheet.write(row, 0, column1_header)
    worksheet.write(row, 1, column2_header)
    row += 1
    # start = row+1
    for vanilla, penalty in zip(column1_data, column2_data):
        worksheet.write(row, col, vanilla)
        worksheet.write(row, col+1, penalty)

        row += 1
    # end = row
    row += 1
    # worksheet.write(row, 0, 'stdvs')
    # worksheet.write(row, 1, 'stdvs')
    # row += 1
    # worksheet.write(row, 0, f'=STDEV.S(A{start}:A{end})')
    row += 1

    return row


main()
