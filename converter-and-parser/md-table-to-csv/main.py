import csv
import argparse
import sys
import os
import re
from pathlib import Path
from typing import List, Optional, Tuple


class MarkdownTableConverter:
    """A robust Markdown table to CSV converter with comprehensive error handling."""
    
    def __init__(self, delimiter: str = '|', strip_empty: bool = True):
        """
        Initialize the converter.
        
        Args:
            delimiter: Character used to separate columns in Markdown
            strip_empty: Whether to strip empty leading/trailing columns
        """
        self.delimiter = delimiter
        self.strip_empty = strip_empty
    
    def read_markdown_file(self, file_path: str) -> str:
        """
        Read Markdown content from a file with proper error handling.
        
        Args:
            file_path: Path to the Markdown file
            
        Returns:
            Content of the file as string
            
        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If file can't be read
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not path.is_file():
            raise ValueError(f"Path is not a file: {file_path}")
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except PermissionError:
            raise PermissionError(f"Permission denied reading file: {file_path}")
        except UnicodeDecodeError:
            # Try with different encoding
            try:
                with open(path, 'r', encoding='latin-1') as f:
                    return f.read()
            except Exception as e:
                raise ValueError(f"Unable to decode file {file_path}: {e}")
    
    def detect_table_format(self, lines: List[str]) -> Tuple[int, int]:
        """
        Detect the header and separator line positions.
        
        Args:
            lines: List of lines from the Markdown content
            
        Returns:
            Tuple of (header_index, separator_index)
            
        Raises:
            ValueError: If table format is invalid
        """
        separator_pattern = re.compile(r'^\s*\|[\s\-:|]+\|\s*$')
        
        for i, line in enumerate(lines):
            if self.delimiter in line and separator_pattern.match(line):
                if i == 0:
                    raise ValueError("Separator line cannot be the first line")
                return i - 1, i
        
        # If no separator found, check if it's a simple table without separator
        for i, line in enumerate(lines):
            if self.delimiter in line:
                return i, -1  # No separator line
        
        raise ValueError("No valid Markdown table found in the content")
    
    def parse_table_row(self, row: str) -> List[str]:
        """
        Parse a single table row, handling edge cases.
        
        Args:
            row: A single row string from the table
            
        Returns:
            List of cell values
        """
        # Split by delimiter
        cells = row.split(self.delimiter)
        
        # Strip whitespace from each cell
        cells = [cell.strip() for cell in cells]
        
        # Remove empty first and last elements (from leading/trailing pipes)
        if self.strip_empty:
            if cells and cells[0] == '':
                cells = cells[1:]
            if cells and cells[-1] == '':
                cells = cells[:-1]
        
        return cells
    
    def validate_table_consistency(self, csv_data: List[List[str]]) -> bool:
        """
        Validate that all rows have the same number of columns.
        
        Args:
            csv_data: Parsed table data
            
        Returns:
            True if consistent, False otherwise
        """
        if not csv_data:
            return False
        
        expected_cols = len(csv_data[0])
        inconsistent_rows = []
        
        for i, row in enumerate(csv_data):
            if len(row) != expected_cols:
                inconsistent_rows.append((i, len(row)))
        
        if inconsistent_rows:
            print(f"Warning: Inconsistent column counts detected:")
            print(f"  Expected: {expected_cols} columns")
            for row_num, col_count in inconsistent_rows:
                print(f"  Row {row_num}: {col_count} columns")
            return False
        
        return True
    
    def extract_tables(self, content: str) -> List[List[List[str]]]:
        """
        Extract multiple tables from Markdown content.
        
        Args:
            content: Markdown content as string
            
        Returns:
            List of tables, where each table is a list of rows
        """
        lines = [line for line in content.strip().split("\n") if line.strip()]
        tables = []
        current_table = []
        in_table = False
        
        separator_pattern = re.compile(r'^\s*\|[\s\-:|]+\|\s*$')
        
        for line in lines:
            if self.delimiter in line:
                if not in_table:
                    in_table = True
                    current_table = []
                
                # Skip separator lines
                if not separator_pattern.match(line):
                    current_table.append(line)
            else:
                if in_table and current_table:
                    # End of current table
                    tables.append(current_table)
                    current_table = []
                in_table = False
        
        # Don't forget the last table
        if current_table:
            tables.append(current_table)
        
        return tables
    
    def convert_to_csv(self, markdown_content: str) -> List[List[str]]:
        """
        Convert Markdown table to CSV data structure.
        
        Args:
            markdown_content: Markdown table as string
            
        Returns:
            List of rows, where each row is a list of cell values
        """
        # Extract tables
        tables = self.extract_tables(markdown_content)
        
        if not tables:
            raise ValueError("No valid Markdown table found")
        
        if len(tables) > 1:
            print(f"Warning: Found {len(tables)} tables. Converting the first one.")
            print("Use --all-tables flag to convert all tables (future feature).")
        
        # Parse the first table
        table_lines = tables[0]
        csv_data = []
        
        for line in table_lines:
            row = self.parse_table_row(line)
            if row:  # Only add non-empty rows
                csv_data.append(row)
        
        return csv_data
    
    def write_csv(self, csv_data: List[List[str]], output_path: str, 
                  dialect: str = 'excel', quoting: int = csv.QUOTE_MINIMAL) -> None:
        """
        Write CSV data to file with proper error handling.
        
        Args:
            csv_data: Data to write
            output_path: Output file path
            dialect: CSV dialect to use
            quoting: Quoting style for CSV writer
        """
        output = Path(output_path)
        
        # Create parent directories if they don't exist
        output.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(output, mode='w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile, dialect=dialect, quoting=quoting)
                writer.writerows(csv_data)
            print(f"✓ CSV file created successfully: {output_path}")
            print(f"  Rows: {len(csv_data)}")
            print(f"  Columns: {len(csv_data[0]) if csv_data else 0}")
        except PermissionError:
            raise PermissionError(f"Permission denied writing to: {output_path}")
        except Exception as e:
            raise IOError(f"Error writing CSV file: {e}")
    
    def convert_file(self, input_path: str, output_path: str, 
                    validate: bool = True) -> None:
        """
        Complete conversion pipeline from Markdown file to CSV file.
        
        Args:
            input_path: Path to input Markdown file
            output_path: Path to output CSV file
            validate: Whether to validate table consistency
        """
        print(f"Reading Markdown file: {input_path}")
        markdown_content = self.read_markdown_file(input_path)
        
        print("Converting to CSV format...")
        csv_data = self.convert_to_csv(markdown_content)
        
        if validate:
            print("Validating table consistency...")
            if not self.validate_table_consistency(csv_data):
                response = input("Continue anyway? (y/n): ")
                if response.lower() != 'y':
                    print("Conversion aborted.")
                    return
        
        print(f"Writing CSV file: {output_path}")
        self.write_csv(csv_data, output_path)


def main():
    """Main function to parse arguments and convert Markdown to CSV."""
    parser = argparse.ArgumentParser(
        description="Convert Markdown tables to CSV format with robust error handling.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.md output.csv
  %(prog)s input.md output.csv --no-validate
  %(prog)s input.md output.csv --delimiter "|"
        """
    )
    
    parser.add_argument(
        "input_file",
        type=str,
        help="Path to the input Markdown file containing table(s)"
    )
    
    parser.add_argument(
        "output_file",
        type=str,
        help="Path to the output CSV file"
    )
    
    parser.add_argument(
        "--delimiter",
        type=str,
        default="|",
        help="Column delimiter character (default: |)"
    )
    
    parser.add_argument(
        "--no-strip-empty",
        action="store_true",
        help="Don't strip empty leading/trailing columns"
    )
    
    parser.add_argument(
        "--no-validate",
        action="store_true",
        help="Skip table consistency validation"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 2.0"
    )
    
    args = parser.parse_args()
    
    try:
        converter = MarkdownTableConverter(
            delimiter=args.delimiter,
            strip_empty=not args.no_strip_empty
        )
        
        converter.convert_file(
            args.input_file,
            args.output_file,
            validate=not args.no_validate
        )
        
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)
    except PermissionError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(3)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(99)


if __name__ == "__main__":
    main()