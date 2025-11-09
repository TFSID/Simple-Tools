#!/usr/bin/env python3
"""
HTML Asset Inliner
Processes HTML files and inlines CSS and JavaScript assets for self-contained distribution.
"""

import os
import re
import sys
from pathlib import Path
from urllib.parse import urljoin, urlparse
import argparse


class AssetInliner:
    def __init__(self, html_path, base_dir=None):
        """
        Initialize the asset inliner.
        
        Args:
            html_path: Path to the HTML file
            base_dir: Base directory for resolving relative paths (defaults to HTML file directory)
        """
        self.html_path = Path(html_path)
        self.base_dir = Path(base_dir) if base_dir else self.html_path.parent
        self.html_content = ""
        self.stats = {"css": 0, "js": 0, "errors": []}
        
    def read_html(self):
        """Read the HTML file content."""
        try:
            with open(self.html_path, 'r', encoding='utf-8') as f:
                self.html_content = f.read()
            return True
        except Exception as e:
            print(f"Error reading HTML file: {e}")
            return False
    
    def resolve_path(self, asset_path):
        """
        Resolve asset path relative to base directory.
        
        Args:
            asset_path: Path from the HTML file
            
        Returns:
            Absolute path to the asset file
        """
        # Skip external URLs
        parsed = urlparse(asset_path)
        if parsed.scheme in ('http', 'https', 'data'):
            return None
            
        # Handle relative paths
        asset_path = asset_path.strip()
        full_path = self.base_dir / asset_path
        
        return full_path if full_path.exists() else None
    
    def read_asset(self, asset_path):
        """Read asset file content."""
        try:
            resolved_path = self.resolve_path(asset_path)
            if resolved_path is None:
                return None
                
            with open(resolved_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            self.stats["errors"].append(f"Error reading {asset_path}: {e}")
            return None
    
    def inline_css(self):
        """Inline all CSS link tags."""
        # Pattern to match <link> tags with CSS stylesheets
        pattern = r'<link\s+([^>]*?)href=["\']([^"\']+)["\']([^>]*?)>'
        
        def replace_css(match):
            full_tag = match.group(0)
            attrs_before = match.group(1)
            href = match.group(2)
            attrs_after = match.group(3)
            
            # Check if it's a stylesheet
            if 'stylesheet' not in attrs_before.lower() and 'stylesheet' not in attrs_after.lower():
                return full_tag
            
            # Try to read and inline the CSS
            css_content = self.read_asset(href)
            if css_content:
                self.stats["css"] += 1
                return f'<style>/* Inlined from: {href} */\n{css_content}\n</style>'
            else:
                # Keep original if file not found or external
                return full_tag
        
        self.html_content = re.sub(pattern, replace_css, self.html_content, flags=re.IGNORECASE)
    
    def inline_js(self):
        """Inline all external JavaScript script tags."""
        # Pattern to match <script> tags with src attribute
        pattern = r'<script\s+([^>]*?)src=["\']([^"\']+)["\']([^>]*?)>\s*</script>'
        
        def replace_js(match):
            full_tag = match.group(0)
            attrs_before = match.group(1)
            src = match.group(2)
            attrs_after = match.group(3)
            
            # Try to read and inline the JS
            js_content = self.read_asset(src)
            if js_content:
                self.stats["js"] += 1
                # Preserve other attributes (like type, async, defer)
                other_attrs = (attrs_before + ' ' + attrs_after).strip()
                # Remove src attribute from other_attrs if present
                other_attrs = re.sub(r'src=["\'][^"\']*["\']', '', other_attrs).strip()
                
                if other_attrs:
                    return f'<script {other_attrs}>/* Inlined from: {src} */\n{js_content}\n</script>'
                else:
                    return f'<script>/* Inlined from: {src} */\n{js_content}\n</script>'
            else:
                # Keep original if file not found or external
                return full_tag
        
        self.html_content = re.sub(pattern, replace_js, self.html_content, flags=re.IGNORECASE | re.DOTALL)
    
    def process(self):
        """Process the HTML file and inline all assets."""
        print(f"Processing: {self.html_path}")
        
        if not self.read_html():
            return False
        
        # Inline CSS files
        print("Inlining CSS files...")
        self.inline_css()
        
        # Inline JavaScript files
        print("Inlining JavaScript files...")
        self.inline_js()
        
        return True
    
    def save(self, output_path=None):
        """
        Save the processed HTML to a file.
        
        Args:
            output_path: Output file path (defaults to adding .inlined before extension)
        """
        if output_path is None:
            stem = self.html_path.stem
            suffix = self.html_path.suffix
            output_path = self.html_path.parent / f"{stem}.inlined{suffix}"
        else:
            output_path = Path(output_path)
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(self.html_content)
            print(f"\n✓ Saved to: {output_path}")
            return True
        except Exception as e:
            print(f"Error saving file: {e}")
            return False
    
    def print_stats(self):
        """Print processing statistics."""
        print("\n" + "="*50)
        print("PROCESSING COMPLETE")
        print("="*50)
        print(f"CSS files inlined: {self.stats['css']}")
        print(f"JS files inlined: {self.stats['js']}")
        
        if self.stats["errors"]:
            print(f"\nErrors encountered: {len(self.stats['errors'])}")
            for error in self.stats["errors"]:
                print(f"  - {error}")
        else:
            print("\n✓ No errors encountered")


def main():
    parser = argparse.ArgumentParser(
        description='Inline CSS and JavaScript assets into HTML files'
    )
    parser.add_argument('html_file', help='Path to the HTML file to process')
    parser.add_argument('-o', '--output', help='Output file path (default: input.inlined.html)')
    parser.add_argument('-b', '--base-dir', help='Base directory for resolving relative paths')
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.html_file):
        print(f"Error: File not found: {args.html_file}")
        sys.exit(1)
    
    # Create inliner and process
    inliner = AssetInliner(args.html_file, args.base_dir)
    
    if inliner.process():
        inliner.save(args.output)
        inliner.print_stats()
    else:
        print("Processing failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()