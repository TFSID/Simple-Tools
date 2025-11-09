#!/usr/bin/env python3
"""
CSS Import Inliner
Processes CSS files and inlines all @import statements into a single CSS file.
"""

import os
import re
import sys
from pathlib import Path
from urllib.parse import urlparse
import argparse


class CSSImportInliner:
    def __init__(self, css_path, base_dir=None, max_depth=10):
        """
        Initialize the CSS import inliner.
        
        Args:
            css_path: Path to the main CSS file
            base_dir: Base directory for resolving relative paths (defaults to CSS file directory)
            max_depth: Maximum recursion depth to prevent circular imports
        """
        self.css_path = Path(css_path)
        self.base_dir = Path(base_dir) if base_dir else self.css_path.parent
        self.css_content = ""
        self.processed_files = set()  # Track processed files to avoid duplicates
        self.max_depth = max_depth
        self.stats = {
            "imports_found": 0,
            "imports_inlined": 0,
            "errors": [],
            "processed_files": []
        }
        
    def read_css(self, css_path=None):
        """Read the CSS file content."""
        if css_path is None:
            css_path = self.css_path
            
        try:
            with open(css_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            error_msg = f"Error reading CSS file {css_path}: {e}"
            self.stats["errors"].append(error_msg)
            return None
    
    def resolve_import_path(self, import_path, current_dir):
        """
        Resolve CSS import path relative to current directory.
        
        Args:
            import_path: Path from the @import statement
            current_dir: Directory of the current CSS file
            
        Returns:
            Absolute path to the imported CSS file or None
        """
        # Remove quotes and url() wrapper
        import_path = import_path.strip().strip('"\'')
        import_path = re.sub(r'^url\(["\']?|["\']?\)$', '', import_path)
        
        # Skip external URLs
        parsed = urlparse(import_path)
        if parsed.scheme in ('http', 'https', 'data'):
            return None
        
        # Resolve relative path
        full_path = current_dir / import_path
        
        if full_path.exists():
            return full_path.resolve()
        else:
            # Try without resolving (might be a different relative path)
            return None
    
    def extract_imports(self, css_content):
        """
        Extract all @import statements from CSS content.
        
        Returns:
            List of tuples: (full_match, import_path)
        """
        # Pattern to match various @import formats:
        # @import url('file.css');
        # @import url("file.css");
        # @import 'file.css';
        # @import "file.css";
        pattern = r'@import\s+(?:url\(["\']?([^"\'()]+)["\']?\)|["\']([^"\']+)["\'])\s*;'
        
        imports = []
        for match in re.finditer(pattern, css_content):
            full_match = match.group(0)
            # Get the path from either capturing group
            import_path = match.group(1) if match.group(1) else match.group(2)
            imports.append((full_match, import_path))
            self.stats["imports_found"] += 1
        
        return imports
    
    def inline_imports(self, css_content, current_dir, depth=0):
        """
        Recursively inline all @import statements.
        
        Args:
            css_content: CSS content to process
            current_dir: Current directory for resolving paths
            depth: Current recursion depth
            
        Returns:
            Processed CSS content with imports inlined
        """
        if depth > self.max_depth:
            self.stats["errors"].append(f"Max recursion depth ({self.max_depth}) reached")
            return css_content
        
        imports = self.extract_imports(css_content)
        
        for full_match, import_path in imports:
            resolved_path = self.resolve_import_path(import_path, current_dir)
            
            if resolved_path is None:
                # Keep the original import if it's external or not found
                if urlparse(import_path).scheme in ('http', 'https'):
                    # Keep external imports as-is
                    continue
                else:
                    self.stats["errors"].append(f"Could not resolve import: {import_path}")
                    continue
            
            # Check if already processed (prevent duplicates)
            if resolved_path in self.processed_files:
                # Remove duplicate import
                css_content = css_content.replace(full_match, f"/* Duplicate import removed: {import_path} */", 1)
                continue
            
            # Mark as processed
            self.processed_files.add(resolved_path)
            self.stats["processed_files"].append(str(resolved_path))
            
            # Read the imported file
            imported_content = self.read_css(resolved_path)
            
            if imported_content is not None:
                # Recursively process imports in the imported file
                imported_dir = resolved_path.parent
                imported_content = self.inline_imports(imported_content, imported_dir, depth + 1)
                
                # Replace the import statement with the file content
                replacement = f"/* ========== Inlined from: {import_path} ========== */\n{imported_content}\n/* ========== End of: {import_path} ========== */\n"
                css_content = css_content.replace(full_match, replacement, 1)
                self.stats["imports_inlined"] += 1
            else:
                # Keep original import if file couldn't be read
                css_content = css_content.replace(full_match, f"/* Error loading: {import_path} */\n{full_match}", 1)
        
        return css_content
    
    def process(self):
        """Process the CSS file and inline all imports."""
        print(f"Processing: {self.css_path}")
        print(f"Base directory: {self.base_dir}")
        print("=" * 60)
        
        # Read main CSS file
        self.css_content = self.read_css()
        if self.css_content is None:
            return False
        
        # Mark main file as processed
        self.processed_files.add(self.css_path.resolve())
        
        # Inline all imports
        print("Inlining @import statements...")
        self.css_content = self.inline_imports(self.css_content, self.base_dir, depth=0)
        
        return True
    
    def save(self, output_path=None):
        """
        Save the processed CSS to a file.
        
        Args:
            output_path: Output file path (defaults to adding .inlined before extension)
        """
        if output_path is None:
            stem = self.css_path.stem
            suffix = self.css_path.suffix
            output_path = self.css_path.parent / f"{stem}.inlined{suffix}"
        else:
            output_path = Path(output_path)
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(self.css_content)
            print(f"\n✓ Saved to: {output_path}")
            return output_path
        except Exception as e:
            print(f"Error saving file: {e}")
            return None
    
    def print_stats(self):
        """Print processing statistics."""
        print("\n" + "=" * 60)
        print("PROCESSING COMPLETE")
        print("=" * 60)
        print(f"Total @import statements found: {self.stats['imports_found']}")
        print(f"Successfully inlined: {self.stats['imports_inlined']}")
        print(f"Unique files processed: {len(self.stats['processed_files'])}")
        
        if self.stats['processed_files']:
            print("\nProcessed files:")
            for i, file_path in enumerate(self.stats['processed_files'], 1):
                print(f"  {i}. {file_path}")
        
        if self.stats["errors"]:
            print(f"\n⚠ Errors encountered: {len(self.stats['errors'])}")
            for error in self.stats["errors"]:
                print(f"  - {error}")
        else:
            print("\n✓ No errors encountered")
        
        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description='Inline CSS @import statements into a single file',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic usage
  python css_inliner.py main.css
  
  # Specify output file
  python css_inliner.py main.css -o bundle.css
  
  # Specify base directory for imports
  python css_inliner.py main.css -b ./assets/css
  
  # Set custom recursion depth
  python css_inliner.py main.css --max-depth 5
        """
    )
    parser.add_argument('css_file', help='Path to the main CSS file to process')
    parser.add_argument('-o', '--output', help='Output file path (default: input.inlined.css)')
    parser.add_argument('-b', '--base-dir', help='Base directory for resolving import paths')
    parser.add_argument('--max-depth', type=int, default=10, 
                        help='Maximum recursion depth (default: 10)')
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.css_file):
        print(f"Error: File not found: {args.css_file}")
        sys.exit(1)
    
    # Create inliner and process
    inliner = CSSImportInliner(args.css_file, args.base_dir, args.max_depth)
    
    if inliner.process():
        output_path = inliner.save(args.output)
        inliner.print_stats()
        
        if output_path:
            print(f"\n✨ Success! Your bundled CSS is ready: {output_path}")
    else:
        print("Processing failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()