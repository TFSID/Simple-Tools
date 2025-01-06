import csv
import argparse

def csv_to_html_table(file_path, output):
    """
    Convert a CSV file into a basic HTML table.

    :param file_path: Path to the CSV file.
    :param output: Path to the output HTML file.
    :return: A string indicating success or an error message.
    """
    try:
        # Read the CSV file
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            rows = list(reader)
        
        if not rows:
            return "The provided CSV file is empty."

        # Ensure each row has the same number of columns as the header
        max_columns = max(len(row) for row in rows)
        for row in rows:
            while len(row) < max_columns:
                row.append("")  # Pad missing columns with empty strings

        # Extract headers and data
        headers = rows[0]
        data = rows[1:]
        
        # Start building the HTML table
        html_table = "<table border='1'>\n<thead>\n<tr>\n"
        
        # Add headers to the HTML table
        for header in headers:
            html_table += f"    <th>{header}</th>\n"
        html_table += "</tr>\n</thead>\n<tbody>\n"
        
        # Add rows to the HTML table
        for row in data:
            html_table += "  <tr>\n"
            for cell in row:
                html_table += f"    <td>{cell}</td>\n"
            html_table += "  </tr>\n"
        
        # Close table
        html_table += "</tbody>\n</table>\n"
        
        # Write the HTML table to the output file
        with open(output, 'w', encoding='utf-8') as f:
            f.write(html_table)
        
        return "HTML table has been created successfully at: " + output
    except FileNotFoundError:
        return f"Error: File '{file_path}' not found."
    except Exception as e:
        return f"An error occurred: {e}"

def main():
    """
    Main function to parse arguments and convert CSV to HTML table.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Convert a CSV file to an HTML table.\n"
            "Usage: python3 csv_to_html_table.py {input_file_path} {output_file_path}"
        )
    )
    parser.add_argument("file_path", type=str, help="Path to the CSV file")
    parser.add_argument("file_output", type=str, help="Path to the output HTML file")
    args = parser.parse_args()

    # Convert CSV to HTML table
    result = csv_to_html_table(args.file_path, args.file_output)
    print(result)

if __name__ == "__main__":
    main()
