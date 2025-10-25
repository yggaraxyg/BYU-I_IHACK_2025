'''
CSV Unparser
Converts an array of arrays into a CSV file
Functions: save_to_csv(output_csv, data_array)
Input: output CSV file name, array of arrays
'''
import csv

def save_to_csv(output_csv, data_array):
    try:
        with open(output_csv, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
            for row in data_array:
                if isinstance(row, list):
                    clean_row = []
                    for item in row:
                        if isinstance(item, list):
                            clean_row.extend(item)
                        else:
                            clean_row.append(str(item))
                    writer.writerow(clean_row)
                else:
                    writer.writerow([str(row)])
        print(f"Successfully saved to {output_csv}")
    except Exception as e:
        print(f"Error saving CSV: {e}")

def save_to_csv_formatted(output_csv, data_array):
    try:
        with open(output_csv, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile, 
                              delimiter=',',
                              quotechar='"',
                              quoting=csv.QUOTE_MINIMAL,
                              escapechar='\\')
            
            for row in data_array:
                if isinstance(row, list):
                    flattened_row = []
                    for item in row:
                        if isinstance(item, list):
                            flattened_row.extend([str(x) for x in item])
                        else:
                            flattened_row.append(str(item).strip())
                    writer.writerow(flattened_row)
                else:
                    writer.writerow([str(row).strip()])
        print(f"Successfully saved formatted CSV to {output_csv}")
    except Exception as e:
        print(f"Error saving formatted CSV: {e}")