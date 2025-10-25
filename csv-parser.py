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
            # skip header row if it follows format of question, answer
            if [cell.lower() for cell in row] == ['question', 'answer']:
                continue
            output_array.append(row)