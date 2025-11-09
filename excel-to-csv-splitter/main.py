#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Skrip ini mengekstrak setiap worksheet dari file Excel (.xlsx) 
dan menyimpannya sebagai file CSV terpisah.

Diperlukan library 'pandas' dan 'openpyxl'.
Anda dapat menginstalnya menggunakan pip:
pip install pandas openpyxl
"""

import pandas as pd
import os

def excel_to_csvs(excel_file_path, output_dir):
    """
    Membaca file Excel dan menyimpan setiap sheet sebagai file CSV di direktori output.
    
    :param excel_file_path: Jalur ke file Excel (input).
    :param output_dir: Direktori untuk menyimpan file CSV (output).
    """
    
    print(f"Memulai proses untuk: {excel_file_path}")
    
    # 1. Periksa apakah file input ada
    if not os.path.exists(excel_file_path):
        print(f"Error: File tidak ditemukan di {excel_file_path}")
        return

    # 2. Buat direktori output jika belum ada
    try:
        os.makedirs(output_dir, exist_ok=True)
        print(f"Direktori output '{output_dir}' siap.")
    except OSError as e:
        print(f"Error: Tidak dapat membuat direktori output '{output_dir}'. {e}")
        return

    # 3. Dapatkan nama file dasar tanpa ekstensi (mis. 'cve_summary_oktober')
    base_excel_name = os.path.splitext(os.path.basename(excel_file_path))[0]

    try:
        # 4. Muat file Excel menggunakan pandas
        # 'sheet_name=None' memberi tahu pandas untuk memuat SEMUA sheet.
        # Ini akan mengembalikan dictionary di mana key adalah nama sheet
        # dan value adalah DataFrame dari sheet tersebut.
        # 'engine='openpyxl'' secara eksplisit digunakan sesuai permintaan.
        print("Membaca file Excel (ini mungkin perlu beberapa saat)...")
        all_sheets = pd.read_excel(excel_file_path, sheet_name=None, engine='openpyxl')
        
        if not all_sheets:
            print("Tidak ada worksheet yang ditemukan dalam file Excel.")
            return

        print(f"Ditemukan {len(all_sheets)} worksheet: {', '.join(all_sheets.keys())}")

        # 5. Iterasi melalui setiap sheet dan simpan sebagai CSV
        for sheet_name, df in all_sheets.items():
            
            # Buat nama file output yang rapi
            # Format: [NamaFileExcelAsal] - [NamaSheet].csv
            # Contoh: cve_summary_oktober - Workarounds_data.csv
            output_csv_name = f"{base_excel_name} - {sheet_name}.csv"
            output_csv_path = os.path.join(output_dir, output_csv_name)
            
            try:
                # Simpan DataFrame ke CSV
                # 'index=False' mencegah pandas menulis indeks baris ke file CSV
                # 'encoding='utf-8'' memastikan kompatibilitas karakter
                df.to_csv(output_csv_path, index=False, encoding='utf-8')
                print(f"  -> Berhasil menyimpan: {output_csv_name}")
                
            except Exception as e:
                print(f"  -> Gagal menyimpan {sheet_name}: {e}")

        print("\nProses ekstraksi selesai.")

    except FileNotFoundError:
        print(f"Error: File input tidak ditemukan di {excel_file_path}")
    except ImportError:
        print("Error: Library 'openpyxl' tidak terinstal. Jalankan 'pip install openpyxl'")
    except Exception as e:
        print(f"Terjadi error yang tidak terduga: {e}")

# --- ---
# Cara Menjalankan Skrip Ini
# --- ---
if __name__ == "__main__":
    
    # --- Ubah variabel ini sesuai kebutuhan Anda ---
    
    # Ganti dengan nama file Excel Anda
    INPUT_FILE = "CyberSec Product Prospect.xlsx" 
    
    # Ganti dengan nama folder tempat Anda ingin menyimpan CSV
    OUTPUT_DIR = "hasil_csv"
    # --- ---
    
    # Memanggil fungsi utama
    excel_to_csvs(INPUT_FILE, OUTPUT_DIR)
