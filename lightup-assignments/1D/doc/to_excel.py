import glob
import xlsxwriter


def get_contents(filename, problem):
    with open(f'./logs/{problem}/{filename}') as file:
        data = file.read().strip().split('\n')
    data = [float(cell) for cell in data]
    return data


def main():

    problems = glob.glob('./problems/d*')

    for file in sorted(problems):

        problem = file.split('/')[-1].split('.')[0]
        workbook = xlsxwriter.Workbook(f'./doc/green3_{problem}.xlsx')

        # Default vs NGSA
        worksheet = workbook.add_worksheet("Default v NSGA")
        cur_row = 0
        col1 = problem + "_run_best_from_gen.log"
        col2 = problem + "_nsga_run_best_from_gen.log"
        cur_row = dump_two_log(problem,
                               'Default', 'NSGA', col1, col2, worksheet, cur_row)

        # Default vs Uniform
        worksheet = workbook.add_worksheet("Default v Uniform")
        cur_row = 0
        col1 = problem + "_run_best_from_gen.log"
        col2 = problem + "_uniform_run_best_from_gen.log"

        cur_row = dump_two_log(problem, 'Default', 'Uniform',
                               col1, col2, worksheet, cur_row)

        # Vanilla v Vanilla Validity
        worksheet = workbook.add_worksheet("NSGA v Uniform")
        cur_row = 0
        col1 = problem + "_nsga_run_best_from_gen.log"
        col2 = problem + "_uniform_run_best_from_gen.log"
        cur_row = dump_two_log(problem,
                               'NSGA', 'Uniform', col1, col2, worksheet, cur_row)

        # Default v Crowding
        worksheet = workbook.add_worksheet("Crowding")
        cur_row = 0
        col1 = problem + "_run_best_from_gen.log"
        col2 = problem + "_crowding_run_best_from_gen.log"

        cur_row = dump_two_log(problem,
                               'Default', 'Crowding', col1, col2, worksheet, cur_row)

        # Default v Sharing
        worksheet = workbook.add_worksheet("Fitness Sharing")
        cur_row = 0
        col1 = problem + "_run_best_from_gen.log"
        col2 = problem + "_sharing_run_best_from_gen.log"

        cur_row = dump_two_log(problem,
                               'Default', 'Fitness Sharing', col1, col2, worksheet, cur_row)

        # Default v 4 Obj
        worksheet = workbook.add_worksheet("Minimize Bulbs")
        cur_row = 0
        col1 = problem + "_run_best_from_gen.log"
        col2 = problem + "_bulb_run_best_from_gen.log"

        cur_row = dump_two_log(problem,
                               'Default', 'Minimize Bulbs', col1, col2, worksheet, cur_row)

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
        worksheet.write(row, col + 1, penalty)

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
