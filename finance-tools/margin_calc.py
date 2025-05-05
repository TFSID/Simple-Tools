import tkinter as tk
from tkinter import messagebox

def calculate_margins():
    try:
        revenue = float(entry_revenue.get())
        hpp = float(entry_hpp.get())
        operasional = float(entry_operasional.get())
        biaya_lain = float(entry_biaya_lain.get())

        # Perhitungan Laba
        laba_kotor = revenue - hpp
        laba_operasi = laba_kotor - operasional
        laba_bersih = laba_operasi - biaya_lain

        # Margin (%)
        margin_kotor = (laba_kotor / revenue) * 100 if revenue else 0
        margin_operasional = (laba_operasi / revenue) * 100 if revenue else 0
        margin_bersih = (laba_bersih / revenue) * 100 if revenue else 0

        # Tampilkan hasil
        hasil.set(
            f"📊 Hasil Kalkulasi Margin & Profit:\n\n"
            f"➡️ Laba Kotor: Rp {laba_kotor:,.0f}  ({margin_kotor:.2f}%)\n"
            f"➡️ Laba Operasional: Rp {laba_operasi:,.0f}  ({margin_operasional:.2f}%)\n"
            f"➡️ Laba Bersih (Total Profit): Rp {laba_bersih:,.0f}  ({margin_bersih:.2f}%)"
        )

    except ValueError:
        messagebox.showerror("Input Tidak Valid", "Masukkan semua nilai dengan angka yang valid.")

# UI Setup
root = tk.Tk()
root.title("Kalkulator Margin & Profit")
root.geometry("460x420")
root.resizable(False, False)

# Input Fields
tk.Label(root, text="Pendapatan (Rp):").pack(pady=(20, 5))
entry_revenue = tk.Entry(root, font=("Arial", 11), width=30)
entry_revenue.pack()

tk.Label(root, text="Harga Pokok Penjualan (HPP) (Rp):").pack(pady=(10, 5))
entry_hpp = tk.Entry(root, font=("Arial", 11), width=30)
entry_hpp.pack()

tk.Label(root, text="Biaya Operasional (Rp):").pack(pady=(10, 5))
entry_operasional = tk.Entry(root, font=("Arial", 11), width=30)
entry_operasional.pack()

tk.Label(root, text="Biaya Lain (Pajak, Bunga, dll.) (Rp):").pack(pady=(10, 5))
entry_biaya_lain = tk.Entry(root, font=("Arial", 11), width=30)
entry_biaya_lain.pack()

# Tombol Hitung
tk.Button(
    root, text="Hitung Margin & Profit",
    command=calculate_margins, bg="#007bff", fg="white", font=("Arial", 11)
).pack(pady=20)

# Output
hasil = tk.StringVar()
tk.Label(
    root, textvariable=hasil, justify="left", font=("Arial", 10),
    bg="#f8f9fa", wraplength=400, padx=10, pady=10, relief="groove"
).pack(padx=10, fill="both", expand=True)

root.mainloop()
