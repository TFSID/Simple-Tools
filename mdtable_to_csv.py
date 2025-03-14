import csv
import argparse

def markdown_to_csv(markdown_table, output_csv_file):

    try:
        with open(markdown_table,'r') as table:
            markdown_table = table.read()
    except Exception as e:
        print(e)
    # Split the Markdown table into lines
    lines = markdown_table.strip().split("\n")

    # Remove the header separator line (e.g., | --- | --- |)
    header = lines[0]
    rows = lines[2:]  # Skipping the separator line
    print(header)
    # print(rows)

    # Prepare data for CSV
    csv_data = []
    # csv_data.append([cell.strip() for cell in header.split("|")[0:-1]])  # Header row with maxsplit length
    csv_data.append([cell.strip() for cell in header.split("|")])  # Header row
    for row in rows:
        # csv_data.append([cell.strip() for cell in row.split("|")[0:-1]]) # rows with maxsplit length
        csv_data.append([cell.strip() for cell in row.split("|")])

    # Write CSV data to a file
    with open(output_csv_file, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerows(csv_data)

    print(f"CSV file '{output_csv_file}' has been created successfully!")

# Example Markdown table
# markdown_table = """
# | Name       | Age | Occupation   |
# |------------|-----|--------------|
# | John Doe   | 28  | Developer    |
# | Jane Smith | 34  | Designer     |
# | Bob Brown  | 45  | Manager      |
# """

# Specify the output CSV file
# output_csv_file = "output.csv"

# Convert Markdown table to CSV
# markdown_to_csv(markdown_table, output_csv_file)


def main():
    """
    Main function to parse arguments and convert Markdown to CSV.
    """
    parser = argparse.ArgumentParser(
        description=
        """
        Convert a Markdown Table to a CSV Format.
        Usage: python3 mdtable_to_csv.py {input_file_path} {output_file_path}
        """
    )
    parser.add_argument("file_path", type=str, help="Path to the CSV file")
    parser.add_argument("file_output", type=str, help="Path to the Output File Path")
    args = parser.parse_args()

    # Convert CSV to Markdown
    csv_list = markdown_to_csv(args.file_path, args.file_output)
    print(csv_list)

if __name__ == "__main__":
    main()