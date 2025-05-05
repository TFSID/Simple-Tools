import tkinter as tk
from tkinter import messagebox

def calculate_selling_price(supplier_price, commission_pct, promo_pct, margin_pct):
    commission_rate = commission_pct / 100
    promo_rate = promo_pct / 100
    margin_rate = margin_pct / 100

    try:
        selling_price = supplier_price / (1 - (commission_rate + promo_rate + margin_rate))
    except ZeroDivisionError:
        return 0, 0, 0

    commission_cost = selling_price * commission_rate
    promo_cost = selling_price * promo_rate
    total_cost = supplier_price + commission_cost + promo_cost
    net_profit = selling_price - total_cost

    return round(selling_price, 2), round(net_profit, 2), round(promo_cost, 2)

def calculate_financial_plan():
    try:
        # Ambil data dari input
        supplier_price = float(entry_supplier.get())
        commission = float(entry_commission.get())
        promo = float(entry_promo.get())
        margin = float(entry_margin.get())
        capital = float(entry_capital.get())
        ops = float(entry_ops.get())
        sample = float(entry_sample.get())
        avg_price = float(entry_avg_price.get())
        units = int(entry_units.get())
        target_profit = float(entry_target_profit.get())

        # Hitung harga jual dan profit
        selling_price, profit_per_unit, promo_budget = calculate_selling_price(
            supplier_price, commission, promo, margin
        )

        # Kalkulasi rencana finansial
        estimated_revenue = avg_price * units
        commission_cost = avg_price * commission / 100
        break_even_units = (capital + ops + sample) / (avg_price - commission_cost)
        estimated_profit = estimated_revenue - (capital + ops + sample)

        # Tampilkan hasil
        output_text.set(
            f"Harga Jual Direkomendasikan: Rp {selling_price:,.0f}\n"
            f"Profit Bersih per Unit: Rp {profit_per_unit:,.0f}\n"
            f"Promo Budget per Unit: Rp {promo_budget:,.0f}\n\n"
            f"--- Rencana Finansial ---\n"
            f"Perkiraan Omzet: Rp {estimated_revenue:,.0f}\n"
            f"Unit Break-Even: {break_even_units:.1f} unit\n"
            f"Estimasi Profit Bulanan: Rp {estimated_profit:,.0f}\n"
            f"Target Profit: {'✅ Tercapai' if estimated_profit >= target_profit else '❌ Belum Tercapai'}"
        )
    except ValueError:
        messagebox.showerror("Error", "Pastikan semua kolom diisi dengan angka valid!")

# Setup UI
root = tk.Tk()
root.title("Kalkulator Finansial Bisnis Fashion Dropship")
root.geometry("600x650")

fields = [
    ("Harga Supplier", "supplier"),
    ("Komisi Platform (%)", "commission"),
    ("Budget Promosi (%)", "promo"),
    ("Margin Laba (%)", "margin"),
    ("Modal Awal", "capital"),
    ("Biaya Operasional/Promosi", "ops"),
    ("Biaya Sample Produk", "sample"),
    ("Harga Rata-Rata Produk", "avg_price"),
    ("Target Penjualan per Bulan (unit)", "units"),
    ("Target Profit", "target_profit")
]

entries = {}
for idx, (label, key) in enumerate(fields):
    tk.Label(root, text=label).grid(row=idx, column=0, sticky="w", padx=10, pady=5)
    entry = tk.Entry(root, width=20)
    entry.grid(row=idx, column=1, padx=10)
    entries[key] = entry

entry_supplier = entries["supplier"]
entry_commission = entries["commission"]
entry_promo = entries["promo"]
entry_margin = entries["margin"]
entry_capital = entries["capital"]
entry_ops = entries["ops"]
entry_sample = entries["sample"]
entry_avg_price = entries["avg_price"]
entry_units = entries["units"]
entry_target_profit = entries["target_profit"]

# Default values
entry_commission.insert(0, "6")
entry_promo.insert(0, "8")
entry_margin.insert(0, "15")

tk.Button(root, text="Hitung", command=calculate_financial_plan, bg="green", fg="white").grid(row=len(fields), column=0, columnspan=2, pady=20)

output_text = tk.StringVar()
output_label = tk.Label(root, textvariable=output_text, justify="left", wraplength=550, bg="#f0f0f0", anchor="nw", padx=10, pady=10, relief="groove")
output_label.grid(row=len(fields)+1, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

root.mainloop()
