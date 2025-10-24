'''
CSV Parser
Functions: parse_csv(input_csv)
Input: CSV file with questions and answers
Output: array of arrays
Output format: [[question, answer], [question, answer], etc]
'''

import csv

# variable for output
output_array = []

# csv parser function
def parse_csv(input_csv):
    with open(input_csv, newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            # skip header row
            if reader.line_num == 1:
                continue
            output_array.append(row)