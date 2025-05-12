import argparse
import os
import sys
import pandas

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

def load_data(filepath):
    if not os.path.exists(filepath):
        print(f"Error: File '{filepath}' not found", file=sys.stderr)
        sys.exit(1)

    ext = os.path.splitext(filepath)[1].lower()
    if ext == ".csv":
        with open(filepath, newline='', encoding='utf-8') as f:
            return list(csv.DictReader(f))
    elif ext == ".json":
        with open(filepath, encoding='utf-8') as f:
            return json.load(f)
    else:
        print("Error: Unsupported file format. Use CSV or JSON", file=sys.stderr)
        sys.exit(1)


def calculator(products, stock_price):
    results = []
    # return results
    supplier_price = stock_price
    admin_pct = 8
    margin_main = 15
    margin_lower = margin_main - 5
    margin_higher = margin_main + 5
    margins = [margin_lower, margin_main, margin_higher]
    try:
        for price in supplier_price:
            for margin in margins
                sp, admin, total_cost, profit = calculate_price(price, margin, admin_pct)
                results.append({
                    "Harga Supplier": round(sp, 2),
                    "MS-2/Unit": round(margin_lower, 2),
                    "MS-3/Unit": round(margin_main, 2),
                    "MS-4/Unit": round(margin_higher, 2),
                    "Harga Jual": round(sp)
                })
        # def format_result(margin, label):
            # return (
                # f"== Margin {margin}% ({label}) ==\n"
                # f"Biaya Admin (8%) : Rp {admin:,.0f}\n"
                # f"Total Biaya      : Rp {total_cost:,.0f}\n"
                # f"Harga Jual       : Rp {sp:,.0f}\n"
                # f"Margin/Keuntungan    : Rp {profit:,.0f}\n"
            # )
        
    except Exception as err:
        # print(f"Error processing item: {item} — {e}", file=sys.stderr)
        return err
    
def save_to_csv(data, output_file):
    if not data:
        print("No data to save.", file=sys.stderr)
        return

    fieldnames = list(data[0].keys())
    with open(output_file, mode="w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)
    print(f"Saved output to: {output_file}")

def parse_args():
    parser = argparse.ArgumentParser(description="Supplier price list margin calculator")
    parser.add_argument("filepath", type=str, help="Input file (.csv or .json)")
    parser.add_argument("--markup", type=float, help="Markup percentage to calculate selling price", required=False)
    parser.add_argument("--output", type=str, help="Output CSV file to save results", default="output_with_margin.csv")
    return parser.parse_args()

def main():
    args = parse_args()
    data = load_data(args.filepath)
    results = calculate_margin(data, markup=args.markup)
    save_to_csv(results, args.output)

if __name__ == "__main__":
    main()