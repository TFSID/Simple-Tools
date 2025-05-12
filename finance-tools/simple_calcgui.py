import tkinter as tk
from tkinter import messagebox

def calculate_price(supplier_price, margin_pct, admin_pct=8):
    margin_rate = margin_pct / 100
    admin_rate = admin_pct / 100

    try:
        # Selling price disesuaikan hanya dengan margin dan admin
        selling_price = supplier_price / (1 - (margin_rate + admin_rate))
    except ZeroDivisionError:
        return 0, 0, 0, 0

    admin_cost = selling_price * admin_rate
    total_cost = supplier_price + admin_cost
    net_profit = selling_price - total_cost

    return (
        round(selling_price, 2),
        round(admin_cost, 2),
        round(total_cost, 2),
        round(net_profit, 2)
    )

def on_calculate():
    try:
        supplier_price = float(entry_supplier.get())
        admin_pct = 8

        margin_main = 15
        margin_lower = margin_main - 5
        margin_higher = margin_main + 5

        def format_result(margin, label):
            sp, admin, total_cost, profit = calculate_price(supplier_price, margin, admin_pct)
            return (
                f"== Margin {margin}% ({label}) ==\n"
                f"Biaya Admin (8%) : Rp {admin:,.0f}\n"
                f"Total Biaya      : Rp {total_cost:,.0f}\n"
                f"Harga Jual       : Rp {sp:,.0f}\n"
                f"Margin/Keuntungan    : Rp {profit:,.0f}\n"
            )

        result.set(
            format_result(margin_main, "utama") + "\n" +
            format_result(margin_lower, "lebih rendah") + "\n" +
            format_result(margin_higher, "lebih tinggi")
        )

    except ValueError:
        messagebox.showerror("Input Tidak Valid", "Masukkan angka yang benar pada harga supplier!")


# UI Setup
root = tk.Tk()
root.title("Kalkulator Harga Jual Produk")
root.geometry("480x550")
root.resizable(False, False)

tk.Label(root, text="Masukkan Harga dari Supplier (Rp)", font=("Arial", 10)).pack(pady=10)
entry_supplier = tk.Entry(root, font=("Arial", 12), width=20)
entry_supplier.pack()

tk.Button(root, text="Hitung Harga Jual", command=on_calculate, bg="#28a745", fg="white", font=("Arial", 11)).pack(pady=15)

result = tk.StringVar()
tk.Label(root, textvariable=result, font=("Arial", 10), justify="left", bg="#f8f9fa", padx=10, pady=10, wraplength=440, relief="groove").pack(padx=10, fill="both", expand=True)

root.mainloop()
