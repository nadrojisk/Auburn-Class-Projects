import glob
import xlsxwriter
import re


def get_contents(filename):
    runs = []
    with open(f'./logs/{filename}') as file:
        contents = file.read()
        for _, run in enumerate(re.split('Run [0-9]*\n', contents)):
            if "Result Log" in run:
                continue
            best_eval_for_run = int(
                run.strip().split('\n')[-1].split('\t')[-1])

            runs.append(best_eval_for_run)
    return runs


def main():

    workbook = xlsxwriter.Workbook(f'./doc/g3/green3.xlsx')

    # Config1 v Config2
    worksheet = workbook.add_worksheet("Default v High")
    col1 = "g2/default_config.log"
    col2 = "g2/high_config.log"
    dump_two_log('Default', 'High', col1, col2, worksheet)

    # Config2 v Config3
    worksheet = workbook.add_worksheet("High v Max")
    col1 = "g2/high_config.log"
    col2 = "g2/max_config.log"
    dump_two_log('High', 'Max', col1, col2, worksheet)

    # Config1 v Config3
    worksheet = workbook.add_worksheet("Default v Max")
    col1 = "g2/default_config.log"
    col2 = "g2/max_config.log"
    dump_two_log('Default', 'Max', col1, col2, worksheet)

    workbook.close()


def dump_two_log(column1_header, column2_header, column1, column2, worksheet):

    column1_data = get_contents(column1)
    column2_data = get_contents(column2)

    write_data(worksheet, column1_header, column2_header,
               column1_data, column2_data)


def write_data(worksheet, column1_header, column2_header, column1_data, column2_data):
    row = 0
    col = 0
    worksheet.write(row, 0, column1_header)
    worksheet.write(row, 1, column2_header)
    row += 1
    # start = row+1
    for vanilla, penalty in zip(column1_data, column2_data):
        worksheet.write(row, col, vanilla)
        worksheet.write(row, col + 1, penalty)

        row += 1
    # end = row
    # row += 1
    # worksheet.write(row, 0, 'stdvs')
    # worksheet.write(row, 1, 'stdvs')
    # row += 1
    # worksheet.write(row, 0, f'=STDEV.S(A{start}:A{end})')
    # row += 1


main()
