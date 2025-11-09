import re
import os
import argparse
from typing import List, Tuple

def extract_icons(content: str) -> List[Tuple[str, str]]:
    """
    Mengekstrak nama ikon dan blok SVG dari konten file sumber.

    Regex ini bekerja dengan cara:
    1.  `case\s+"([^"]+)"`: Mencocokkan 'case "', lalu menangkap (grup 1) nama ikon
        yang terdiri dari karakter apa pun kecuali tanda kutip.
    2.  `.*?`: Mencocokkan karakter apa pun di antara nama dan tag <svg> secara non-greedy.
    3.  `(<svg.*?</svg>)`: Menangkap (grup 2) seluruh blok SVG, dari tag pembuka hingga penutup.
    4.  Flag `re.DOTALL` memastikan bahwa `.` juga mencocokkan baris baru, yang penting
        karena blok SVG mencakup beberapa baris.

    Args:
        content: String berisi konten file sumber (JSX/TSX).

    Returns:
        Sebuah list berisi tuple, di mana setiap tuple berisi (nama_ikon, konten_svg).
    """
    # Pola regex untuk menemukan setiap ikon dalam switch case
    pattern = re.compile(
        r'case\s+"([^"]+)":.*?return\s*\(.*?((<svg.*?</svg>)).*?\);',
        re.DOTALL
    )
    
    # Menemukan semua kecocokan. findall akan mengembalikan tuple dari capturing groups.
    # Grup pertama ([^"]+) adalah nama ikon.
    # Grup kedua ((<svg.*?</svg>)) adalah blok SVG lengkap.
    matches = pattern.findall(content)
    
    # Kita hanya perlu nama dan blok svg utama.
    # Pola di atas memiliki grup bersarang, jadi kita akan mengambil grup yang relevan.
    # Grup 1 adalah nama ikon, Grup 3 adalah blok <svg> itu sendiri.
    
    # Mari kita sederhanakan polanya untuk menghindari grup yang terlalu banyak bersarang.
    simplified_pattern = re.compile(
        r'case\s+"([^"]+)":.*?<svg(.*?)<\/svg>',
        re.DOTALL
    )
    
    # Regex yang lebih robust yang menangkap seluruh tag svg
    robust_pattern = re.compile(
        r'case\s+"([^"]+)":.*?return\s*\(\s*(<svg.*?<\/svg>)\s*\);',
        re.DOTALL
    )

    return robust_pattern.findall(content)

def clean_svg_content(svg_content: str) -> str:
    """
    Membersihkan konten SVG dari atribut khusus JSX.

    Args:
        svg_content: String berisi konten SVG.

    Returns:
        String SVG yang sudah dibersihkan.
    """
    # Menghapus atribut className={props.className} beserta spasi di sekitarnya.
    # Ini penting karena atribut ini tidak valid dalam file .svg standar.
    cleaned_svg = re.sub(r'\s*className=\{props\.className\}\s*', '', svg_content, flags=re.IGNORECASE)
    
    # Menghapus atribut fillRule dan clipRule jika nilainya "evenodd"
    # Ini seringkali default dan tidak diperlukan untuk tampilan.
    cleaned_svg = re.sub(r'\s*fillRule="evenodd"', '', cleaned_svg)
    cleaned_svg = re.sub(r'\s*clipRule="evenodd"', '', cleaned_svg)
    
    # Memastikan tidak ada spasi berlebih di dalam tag svg pembuka
    cleaned_svg = re.sub(r'<svg\s+>', '<svg>', cleaned_svg)
    
    return cleaned_svg.strip()

def save_icons_to_files(icons: List[Tuple[str, str]], output_dir: str):
    """
    Menyimpan setiap ikon ke dalam file .svg terpisah.

    Args:
        icons: List berisi tuple (nama_ikon, konten_svg).
        output_dir: Direktori tujuan untuk menyimpan file SVG.
    """
    # Membuat direktori output jika belum ada
    os.makedirs(output_dir, exist_ok=True)
    
    if not icons:
        print("⚠️ Tidak ada ikon yang ditemukan. Pastikan format file sumber sudah benar.")
        return

    print(f"🔍 Menemukan {len(icons)} ikon. Memulai proses ekspor...")
    
    count = 0
    for icon_name, svg_content in icons:
        # Membersihkan konten SVG dari sintaks JSX
        cleaned_svg = clean_svg_content(svg_content)
        
        # Membuat nama file (contoh: Check.svg)
        file_name = f"{icon_name}.svg"
        output_path = os.path.join(output_dir, file_name)
        
        try:
            # Menulis konten SVG yang sudah dibersihkan ke file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(cleaned_svg)
            print(f"✅ Berhasil mengekspor: {file_name}")
            count += 1
        except IOError as e:
            print(f"❌ Gagal menyimpan {file_name}: {e}")

    print(f"\n✨ Selesai! Berhasil mengekspor {count} dari {len(icons)} ikon ke direktori '{output_dir}'.")


def main():
    """Fungsi utama untuk menjalankan skrip."""
    parser = argparse.ArgumentParser(
        description="Ekstrak ikon SVG dari file komponen React/TypeScript dan simpan sebagai file .svg terpisah.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    
    parser.add_argument(
        "input_file",
        help="Path ke file sumber .tsx yang berisi definisi ikon."
    )
    
    parser.add_argument(
        "-o", "--output-dir",
        default="exported_icons",
        help="Direktori untuk menyimpan file .svg yang diekspor (default: exported_icons)."
    )
    
    args = parser.parse_args()
    
    try:
        # Membaca seluruh konten dari file input
        with open(args.input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File tidak ditemukan di '{args.input_file}'")
        return
    except Exception as e:
        print(f"Error saat membaca file: {e}")
        return
        
    # Mengekstrak ikon dari konten
    icons_data = extract_icons(content)
    
    # Menyimpan ikon ke dalam file-file
    save_icons_to_files(icons_data, args.output_dir)

if __name__ == "__main__":
    main()
