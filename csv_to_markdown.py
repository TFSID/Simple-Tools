import csv
import argparse

def calculate_column_widths(data):
    """
    Calculate the maximum width of each column based on the content.
    """
    widths = [len(header) for header in data[0]]  # Start with header lengths
    for row in data[1:]:
        widths = [max(width, len(cell)) for width, cell in zip(widths, row)]
    return widths

def csv_to_markdown(file_path,output):
    """
    Convert a CSV file into Markdown table format.

    :param file_path: Path to the CSV file.
    :return: A string representing the Markdown table.
    """
    try:
        # Read the CSV file
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            rows = list(reader)
        
        if not rows:
            return "The provided CSV file is empty."
        
        # Wrap the second column first before formatting (hooks column)
        # for row in rows[1:]:
        #     if len(row) > 1:
        #         row[1] = f"``{row[1]}``"
        
        # Calculate column widths
        column_widths = calculate_column_widths(rows)
        
        # Extract headers and data
        headers = rows[0]
        data = rows[1:]
        
        # Row Formatting
        def format_row(row):
            # row = [f"``{cell}``" if index == 1 else cell for index, cell in enumerate(row)]
            return " | ".join(f"{cell:<{width}}" for cell, width in zip(row, column_widths))

        # Build Markdown table
        
        markdown_table = []
        markdown_table.append(format_row(headers))
        markdown_table.append(" | ".join("-" * width for width in column_widths))  # Separator
        for row in data:
            markdown_table.append(format_row(row))
        
        # header_row = "| " + " | ".join(headers) + " |"
        # separator_row = "| " + " | ".join(["---"] * len(headers)) + " |"
        # data_rows = "\n".join("| " + " | ".join(row) + " |" for row in data)
        # result = f"{header_row}\n{separator_row}\n{data_rows}"
        with open(output,'w') as f:
            f.write("\n".join(markdown_table))
        return "Output Written At: " + output
    except FileNotFoundError:
        return f"Error: File '{file_path}' not found."
    except Exception as e:
        return f"An error occurred: {e}"

def main():
    """
    Main function to parse arguments and convert CSV to Markdown.
    """
    parser = argparse.ArgumentParser(
        description=
        """
        Convert a CSV file to a formatted Markdown table.
        Usage: python3 csv_to_markdown.py {input_file_path} {output_file_path}
        """
    )
    parser.add_argument("file_path", type=str, help="Path to the CSV file")
    parser.add_argument("file_output", type=str, help="Path to the Output File Path")
    args = parser.parse_args()

    # Convert CSV to Markdown
    markdown_table = csv_to_markdown(args.file_path, args.file_output)
    print(markdown_table)

if __name__ == "__main__":
    main()
