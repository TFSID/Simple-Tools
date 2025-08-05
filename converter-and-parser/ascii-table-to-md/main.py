import re

def parse_ascii_table(ascii_table):
    lines = ascii_table.strip().splitlines()

    # Remove border lines and empty lines
    data_lines = [line for line in lines if line.strip().startswith('|')]

    # Split each line into columns based on pipe characters
    split_lines = [re.split(r'\s*\|\s*', line.strip('| ')) for line in data_lines]

    # Prepare a list to hold parsed rows
    rows = []
    current_row = []

    for line in split_lines:
        if all(cell == '' for cell in line):
            continue

        if not any(cell.strip() for cell in line[:3]) and current_row:
            # If the first few cells are empty, it's a continuation
            for i, cell in enumerate(line):
                if cell.strip():
                    current_row[i] += ' ' + cell.strip()
        else:
            if current_row:
                rows.append(current_row)
            current_row = [cell.strip() for cell in line]

    # Append the last row
    if current_row:
        rows.append(current_row)

    return rows

def to_markdown_table(rows):
    # Determine the maximum number of columns
    num_cols = max(len(row) for row in rows)

    # Pad all rows to the same length
    for row in rows:
        row += [''] * (num_cols - len(row))

    # Prepare Markdown header
    header = rows[0]
    separator = ['---'] * num_cols
    body = rows[1:]

    markdown = ['| ' + ' | '.join(header) + ' |']
    markdown.append('| ' + ' | '.join(separator) + ' |')

    for row in body:
        markdown.append('| ' + ' | '.join(row) + ' |')

    return '\n'.join(markdown)

# Read ASCII table (replace this with reading from a file if needed)

with open("sample.txt", "r") as f:
    ascii_table = f.read()
# ascii_table = """<PASTE YOUR ASCII TABLE HERE>"""

# Convert to Markdown
parsed_rows = parse_ascii_table(ascii_table)
markdown_table = to_markdown_table(parsed_rows)

# Output
print(markdown_table)

# Optionally save to file
with open("converted_table.md", "w") as f:
    f.write(markdown_table)
