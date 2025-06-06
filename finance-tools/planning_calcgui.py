import tkinter as tk
from tkinter import messagebox

def calculate_target_sales():
    try:
        capital = float(entry_capital.get())
        ops = float(entry_ops.get())
        avg_price = float(entry_avg_price.get())
        target_profit = float(entry_target_profit.get())

        total_modal = capital + ops
        total_income_needed = total_modal + target_profit

        if avg_price <= 0:
            raise ValueError("Harga rata-rata harus lebih dari 0.")

        # Margin rates
        margin_5 = 5 / 100
        margin_10 = 10 / 100
        margin_20 = 20 / 100

        # Hitung harga jual per unit berdasarkan margin
        selling_5 = avg_price / (1 - margin_5)
        selling_10 = avg_price / (1 - margin_10)
        selling_20 = avg_price / (1 - margin_20)

        # Hitung jumlah unit yang harus terjual
        units_5 = total_income_needed / selling_5
        units_10 = total_income_needed / selling_10
        units_20 = total_income_needed / selling_20

        result.set(
            f"--- Hasil Perhitungan ---\n"
            f"Total Modal        : Rp {total_modal:,.0f}\n"
            f"Target Omzet       : Rp {total_income_needed:,.0f}\n\n"
            f"== Dengan Margin 5% ==\n"
            f"Harga Jual / Unit  : Rp {selling_5:,.0f}\n"
            f"Unit Dibutuhkan    : {units_5:.1f} unit\n\n"
            f"== Dengan Margin 10% ==\n"
            f"Harga Jual / Unit  : Rp {selling_10:,.0f}\n"
            f"Unit Dibutuhkan    : {units_10:.1f} unit\n\n"
            f"== Dengan Margin 20% ==\n"
            f"Harga Jual / Unit  : Rp {selling_20:,.0f}\n"
            f"Unit Dibutuhkan    : {units_20:.1f} unit"
        )

    except ValueError:
        messagebox.showerror("Input Tidak Valid", "Pastikan semua kolom diisi dengan angka yang valid!")

# UI Setup
root = tk.Tk()
root.title("Kalkulator Target Penjualan")
root.geometry("500x600")
root.resizable(False, False)

tk.Label(root, text="Modal Awal (Rp)", font=("Arial", 10)).pack(pady=5)
entry_capital = tk.Entry(root, font=("Arial", 11))
entry_capital.pack()

tk.Label(root, text="Modal Operasional (Rp)", font=("Arial", 10)).pack(pady=5)
entry_ops = tk.Entry(root, font=("Arial", 11))
entry_ops.pack()

tk.Label(root, text="Harga Produk Rata-Rata (Rp)", font=("Arial", 10)).pack(pady=5)
entry_avg_price = tk.Entry(root, font=("Arial", 11))
entry_avg_price.pack()

tk.Label(root, text="Target Profit yang Diinginkan (Rp)", font=("Arial", 10)).pack(pady=5)
entry_target_profit = tk.Entry(root, font=("Arial", 11))
entry_target_profit.pack()

tk.Button(root, text="Hitung Target Penjualan", command=calculate_target_sales, bg="#007bff", fg="white", font=("Arial", 11)).pack(pady=15)

result = tk.StringVar()
tk.Label(root, textvariable=result, justify="left", font=("Arial", 10), wraplength=450, bg="#f1f1f1", padx=10, pady=10, relief="groove").pack(padx=10, fill="both", expand=True)

root.mainloop()
