#!/usr/bin/env python3
"""
Icon SVG Exporter
=================
Script untuk mengekstrak dan mengekspor SVG icons dari React/TypeScript codebase
ke file SVG individual dengan fitur validasi dan error handling yang robust.

Author: Assistant
Version: 1.0.0
"""

import re
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from xml.etree import ElementTree as ET
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('icon_export.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class IconExtractor:
    """Class untuk mengekstrak dan memvalidasi SVG icons dari kode React"""
    
    def __init__(self, source_code: str, output_dir: str = "exported_icons"):
        self.source_code = source_code
        self.output_dir = Path(output_dir)
        self.icons: Dict[str, str] = {}
        self.errors: List[str] = []
        
    def extract_icon_names(self) -> List[str]:
        """Ekstrak semua nama icon dari type definition"""
        pattern = r'type Icon =\s*\|?\s*"([^"]+)"(?:\s*\|\s*"([^"]+)")*'
        matches = re.finditer(r'\|\s*"([^"]+)"', self.source_code)
        icon_names = [match.group(1) for match in matches]
        
        # Fallback: cari dari case statements
        if not icon_names:
            pattern = r'case\s+"([^"]+)":'
            matches = re.finditer(pattern, self.source_code)
            icon_names = [match.group(1) for match in matches]
        
        logger.info(f"Ditemukan {len(icon_names)} icon names")
        return icon_names
    
    def extract_svg_for_icon(self, icon_name: str) -> Optional[str]:
        """Ekstrak SVG content untuk icon tertentu"""
        # Pattern untuk match case statement dan SVG content
        pattern = rf'case\s+"{icon_name}":\s*return\s*\(([\s\S]*?)\);'
        match = re.search(pattern, self.source_code)
        
        if not match:
            logger.warning(f"Tidak dapat menemukan SVG untuk icon: {icon_name}")
            self.errors.append(f"Missing SVG: {icon_name}")
            return None
        
        svg_content = match.group(1).strip()
        
        # Clean up: hapus className prop karena tidak diperlukan di SVG standalone
        svg_content = re.sub(r'className=\{props\.className\}', '', svg_content)
        
        # Normalize whitespace
        svg_content = re.sub(r'\s+', ' ', svg_content)
        svg_content = re.sub(r'>\s+<', '><', svg_content)
        
        return svg_content.strip()
    
    def validate_svg(self, svg_content: str, icon_name: str) -> bool:
        """Validasi apakah SVG content valid"""
        try:
            # Tambahkan namespace jika tidak ada
            if 'xmlns=' not in svg_content:
                svg_content = svg_content.replace('<svg', '<svg xmlns="http://www.w3.org/2000/svg"', 1)
            
            # Parse XML untuk validasi
            ET.fromstring(svg_content)
            return True
        except ET.ParseError as e:
            logger.error(f"SVG tidak valid untuk {icon_name}: {e}")
            self.errors.append(f"Invalid SVG for {icon_name}: {e}")
            return False
    
    def format_svg(self, svg_content: str, icon_name: str) -> str:
        """Format SVG dengan proper indentation dan metadata"""
        try:
            # Parse SVG
            root = ET.fromstring(svg_content)
            
            # Tambahkan comment dengan metadata
            comment = f" Icon: {icon_name} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} "
            
            # Format dengan indentation
            self._indent_xml(root)
            
            # Convert back to string
            formatted_svg = ET.tostring(root, encoding='unicode', method='xml')
            
            # Tambahkan XML declaration dan comment
            result = f'<?xml version="1.0" encoding="UTF-8"?>\n<!--{comment}-->\n{formatted_svg}'
            
            return result
        except Exception as e:
            logger.warning(f"Tidak dapat memformat SVG untuk {icon_name}, menggunakan original: {e}")
            return svg_content
    
    def _indent_xml(self, elem, level=0):
        """Helper function untuk indentasi XML"""
        indent = "\n" + "  " * level
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = indent + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = indent
            for child in elem:
                self._indent_xml(child, level + 1)
            if not child.tail or not child.tail.strip():
                child.tail = indent
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = indent
    
    def extract_all_icons(self) -> Dict[str, str]:
        """Ekstrak semua icons dari source code"""
        logger.info("Memulai ekstraksi icons...")
        
        icon_names = self.extract_icon_names()
        
        for icon_name in icon_names:
            svg_content = self.extract_svg_for_icon(icon_name)
            
            if svg_content:
                # Pastikan ada namespace xmlns
                if 'xmlns=' not in svg_content:
                    svg_content = svg_content.replace('<svg', '<svg xmlns="http://www.w3.org/2000/svg"', 1)
                
                if self.validate_svg(svg_content, icon_name):
                    formatted_svg = self.format_svg(svg_content, icon_name)
                    self.icons[icon_name] = formatted_svg
                    logger.info(f"✓ Berhasil ekstrak: {icon_name}")
                else:
                    logger.error(f"✗ Gagal validasi: {icon_name}")
        
        logger.info(f"\nTotal berhasil diekstrak: {len(self.icons)}/{len(icon_names)} icons")
        return self.icons
    
    def export_to_files(self, create_index: bool = True) -> None:
        """Export icons ke file SVG individual"""
        if not self.icons:
            logger.error("Tidak ada icon untuk diekspor. Jalankan extract_all_icons() terlebih dahulu.")
            return
        
        # Buat output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"\nMengekspor icons ke: {self.output_dir.absolute()}")
        
        # Export setiap icon
        exported_count = 0
        for icon_name, svg_content in self.icons.items():
            # Buat filename (convert camelCase to kebab-case)
            filename = self._to_kebab_case(icon_name) + '.svg'
            filepath = self.output_dir / filename
            
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(svg_content)
                exported_count += 1
                logger.info(f"  → {filename}")
            except Exception as e:
                logger.error(f"Gagal menulis file {filename}: {e}")
                self.errors.append(f"Export failed for {icon_name}: {e}")
        
        logger.info(f"\n✓ Berhasil ekspor {exported_count} file SVG")
        
        # Buat index/manifest file
        if create_index:
            self._create_index_file()
    
    def _to_kebab_case(self, text: str) -> str:
        """Convert camelCase/PascalCase to kebab-case"""
        # Insert hyphen before uppercase letters
        kebab = re.sub('([a-z0-9])([A-Z])', r'\1-\2', text)
        return kebab.lower()
    
    def _create_index_file(self) -> None:
        """Buat index file yang berisi daftar semua icons"""
        index_path = self.output_dir / 'INDEX.md'
        
        with open(index_path, 'w', encoding='utf-8') as f:
            f.write("# Exported Icons Index\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"**Total Icons:** {len(self.icons)}\n\n")
            f.write("## Icon List\n\n")
            f.write("| Icon Name | Filename | Status |\n")
            f.write("|-----------|----------|--------|\n")
            
            for icon_name in sorted(self.icons.keys()):
                filename = self._to_kebab_case(icon_name) + '.svg'
                f.write(f"| {icon_name} | `{filename}` | ✓ |\n")
            
            if self.errors:
                f.write("\n## Errors\n\n")
                for error in self.errors:
                    f.write(f"- {error}\n")
        
        logger.info(f"✓ Index file dibuat: {index_path}")
    
    def generate_report(self) -> str:
        """Generate summary report"""
        report = "\n" + "="*60 + "\n"
        report += "ICON EXTRACTION REPORT\n"
        report += "="*60 + "\n\n"
        report += f"Total Icons Extracted: {len(self.icons)}\n"
        report += f"Output Directory: {self.output_dir.absolute()}\n"
        
        if self.errors:
            report += f"\nErrors Encountered: {len(self.errors)}\n"
            for error in self.errors[:5]:  # Show first 5 errors
                report += f"  - {error}\n"
            if len(self.errors) > 5:
                report += f"  ... and {len(self.errors) - 5} more\n"
        else:
            report += "\n✓ No errors encountered!\n"
        
        report += "\n" + "="*60 + "\n"
        return report


def main():
    """Main function"""
    # Baca source code dari file atau string
    # Untuk demo, kita load dari clipboard atau file
    
    try:
        # Coba baca dari file jika disediakan
        if len(sys.argv) > 1:
            source_file = Path(sys.argv[1])
            with open(source_file, 'r', encoding='utf-8') as f:
                source_code = f.read()
            logger.info(f"Membaca dari file: {source_file}")
        else:
            # Placeholder - dalam praktik nyata, paste code di sini
            logger.error("Silakan provide source file sebagai argument: python script.py <source_file>")
            return
        
        # Tentukan output directory
        output_dir = sys.argv[2] if len(sys.argv) > 2 else "exported_icons"
        
        # Buat extractor dan jalankan
        extractor = IconExtractor(source_code, output_dir)
        extractor.extract_all_icons()
        extractor.export_to_files(create_index=True)
        
        # Print report
        print(extractor.generate_report())
        
        logger.info("✓ Proses selesai!")
        
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()