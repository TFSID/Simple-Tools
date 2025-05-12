import argparse
import os
import sys
import csv
import json

def calculate_price(supplier_price, margin_pct, admin_pct=8):
    margin_rate = margin_pct / 100
    admin_rate = admin_pct / 100

    try:
        selling_price = supplier_price / (1 - (margin_rate + admin_rate))
    except ZeroDivisionError:
        return 0, 0, 0, 0

    admin_cost = selling_price * admin_rate
    total_cost = supplier_price + admin_cost
    net_profit = selling_price - total_cost

    # Menghasilkan bilangan bulat tanpa Koma
    return (
        round(selling_price),
        round(admin_cost),
        round(total_cost),
        round(net_profit)
    )

    # return (
    #     round(selling_price, 2),
    #     round(admin_cost, 2),
    #     round(total_cost, 2),
    #     round(net_profit, 2)
    # )

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

def calculator(products, admin_pct=8, margin_main=15):
    results = []
    margin_lower = margin_main - 5
    margin_higher = margin_main + 5
    margins = [margin_lower, margin_main, margin_higher]

    for item in products:
        try:
            product_name = item.get("Product", item.get("name", "Unnamed Product"))
            price_str = item.get("Harga Supplier", item.get("price", item.get("harga", "0")))
            supplier_price = float(price_str)

            result = {
                "Product": product_name,
                "Harga Supplier": supplier_price,
            }

            for margin in margins:
                sp, admin, total_cost, profit = calculate_price(supplier_price, margin, admin_pct)
                label = f"MS-{margin:.0f}%"
                result[f"{label} Harga Jual"] = sp
                result[f"{label} Profit"] = profit

                if margin == margin_main:
                    result["Harga Jual"] = sp  # Kolom utama harga jual

            results.append(result)

        except Exception as err:
            print(f"Error processing item '{item}': {err}", file=sys.stderr)

    return results

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
    parser.add_argument("--margin", type=float, default=15, help="Main margin percentage (default: 15%)")
    parser.add_argument("--admin", type=float, default=8, help="Admin cost percentage (default: 8%)")
    parser.add_argument("--output", type=str, default="output_with_margin.csv", help="Output CSV file to save results")
    return parser.parse_args()

def main():
    args = parse_args()
    data = load_data(args.filepath)
    results = calculator(data, admin_pct=args.admin, margin_main=args.margin)
    save_to_csv(results, args.output)

if __name__ == "__main__":
    main()
