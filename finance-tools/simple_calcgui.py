import tkinter as tk
from tkinter import messagebox

def calculate_price(supplier_price, commission_pct, margin_pct):
    commission_rate = commission_pct / 100
    margin_rate = margin_pct / 100

    try:
        selling_price = supplier_price / (1 - (commission_rate + margin_rate))
    except ZeroDivisionError:
        return 0, 0

    commission_cost = selling_price * commission_rate
    total_cost = supplier_price + commission_cost
    net_profit = selling_price - total_cost

    return round(selling_price, 2), round(net_profit, 2)

def on_calculate():
    try:
        supplier_price = float(entry_supplier.get())
        commission_pct = 6  # default komisi

        margin_main = 15
        margin_lower = margin_main - 5
        margin_higher = margin_main + 5

        sp_main, profit_main = calculate_price(supplier_price, commission_pct, margin_main)
        sp_low, profit_low = calculate_price(supplier_price, commission_pct, margin_lower)
        sp_high, profit_high = calculate_price(supplier_price, commission_pct, margin_higher)

        result.set(
            f"== Margin {margin_main}% ==\n"
            f"Harga Jual: Rp {sp_main:,.0f}\n"
            f"Profit/Unit: Rp {profit_main:,.0f}\n\n"
            f"== Margin {margin_lower}% (lebih rendah) ==\n"
            f"Harga Jual: Rp {sp_low:,.0f}\n"
            f"Profit/Unit: Rp {profit_low:,.0f}\n\n"
            f"== Margin {margin_higher}% (lebih tinggi) ==\n"
            f"Harga Jual: Rp {sp_high:,.0f}\n"
            f"Profit/Unit: Rp {profit_high:,.0f}\n"
        )
    except ValueError:
        messagebox.showerror("Input Tidak Valid", "Masukkan angka yang benar pada harga supplier!")

# UI Setup
root = tk.Tk()
root.title("Kalkulator Harga Jual Produk")
root.geometry("450x420")
root.resizable(False, False)

tk.Label(root, text="Masukkan Harga dari Supplier (Rp)", font=("Arial", 10)).pack(pady=10)
entry_supplier = tk.Entry(root, font=("Arial", 12), width=20)
entry_supplier.pack()

tk.Button(root, text="Hitung Harga Jual", command=on_calculate, bg="#28a745", fg="white", font=("Arial", 11)).pack(pady=15)

result = tk.StringVar()
tk.Label(root, textvariable=result, font=("Arial", 10), justify="left", bg="#f8f9fa", padx=10, pady=10, wraplength=400, relief="groove").pack(padx=10, fill="both", expand=True)

root.mainloop()
