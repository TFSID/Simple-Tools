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
        
        margin_rate = 10 / 100  # 10% margin
        margin_rate_lower = 5 / 100  # 5% margin
        margin_rate_higher = 20 / 100  # 10% margin

        # Tambahkan Harga Jual Produk dengan Margin 10% per unit
        selling_price = avg_price * margin_rate
        
        # Tambahkan Harga Jual Produk dengan Margin 5% per unit
        selling_price_lower = avg_price / margin_rate_lower

        # Tambahkan Harga Jual Produk dengan Margin 20% per unit
        selling_price_higher = avg_price * margin_rate_higher

        # units_needed = total_income_needed / avg_price
        units_needed = total_income_needed / selling_price
        units_needed_lower = total_income_needed / selling_price_lower
        units_needed_higher = total_income_needed / selling_price_higher
        
        result.set(
            f"--- Hasil Perhitungan ---\n"
            f"Total Modal: Rp {total_modal:,.0f}\n"
            f"Target Omzet: Rp {total_income_needed:,.0f}\n"
            # f"Unit yang Harus Terjual: {units_needed:.1f} unit\n"
            f"Unit yang Harus Terjual Jika Margin 20%: {units_needed_higher:.1f} unit\n"
            f"Unit yang Harus Terjual Jika Margin 10%: {units_needed:.1f} unit\n"
            f"Unit yang Harus Terjual Jika Margin 5%: {units_needed_lower:.1f} unit\n"
            f"Status: {'✅ Target Profit Tercapai' if units_needed * selling_price >= total_income_needed else '❌ Belum Tercapai'}"
        )
    except ValueError:
        messagebox.showerror("Input Tidak Valid", "Pastikan semua kolom diisi dengan angka yang valid!")

# UI Setup
root = tk.Tk()
root.title("Kalkulator Target Penjualan")
root.geometry("500x400")
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
