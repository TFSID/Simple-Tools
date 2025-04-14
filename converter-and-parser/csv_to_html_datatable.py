import csv
import argparse

def csv_to_html(file_path, output):
    """
    Convert a CSV file into an HTML DataTable.

    :param file_path: Path to the CSV file.
    :param output: Path to the output HTML file.
    :return: A string indicating success or an error message.
    """
    try:
        # Read the CSV file
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"', skipinitialspace=True)
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
        html_table = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>CSV to DataTable</title>
            <link rel="stylesheet" href="https://cdn.datatables.net/1.13.5/css/jquery.dataTables.min.css">
            <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
            <script src="https://cdn.datatables.net/1.13.5/js/jquery.dataTables.min.js"></script>
        </head>
        <body>
        <table id="dataTable" class="display" style="width:100%">
        <thead>
        <tr>
        """
        
        # Add headers to the HTML table
        for header in headers:
            html_table += f"<th>{header}</th>"
        html_table += "</tr></thead><tbody>"
        
        # Add rows to the HTML table
        for row in data:
            html_table += "<tr>"
            for cell in row:
                html_table += f"<td>{cell}</td>"
            html_table += "</tr>"
        
        # Close table and add DataTable initialization script
        html_table += """
        </tbody>
        </table>
        <script>
            $(document).ready(function() {
                $('#dataTable').DataTable();
            });
        </script>
        </body>
        </html>
        """
        
        # Write the HTML table to the output file
        with open(output, 'w', encoding='utf-8') as f:
            f.write(html_table)
        
        return "HTML DataTable has been created successfully at: " + output
    except FileNotFoundError:
        return f"Error: File '{file_path}' not found."
    except Exception as e:
        return f"An error occurred: {e}"

def main():
    """
    Main function to parse arguments and convert CSV to HTML DataTable.
    """
    parser = argparse.ArgumentParser(
        description=(
            "Convert a CSV file to an HTML DataTable.\n"
            "Usage: python3 csv_to_html.py {input_file_path} {output_file_path}"
        )
    )
    parser.add_argument("file_path", type=str, help="Path to the CSV file")
    parser.add_argument("file_output", type=str, help="Path to the output HTML file")
    args = parser.parse_args()

    # Convert CSV to HTML DataTable
    result = csv_to_html(args.file_path, args.file_output)
    print(result)

if __name__ == "__main__":
    main()
