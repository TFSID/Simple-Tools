import argparse

def calculate_selling_price(supplier_price, commission_pct, promo_pct, margin_pct):
    """
    Calculates the selling price, net profit, and ad recovery based on given percentages.
    """
    # Convert percentages to decimals
    commission_rate = commission_pct / 100
    promo_rate = promo_pct / 100
    margin_rate = margin_pct / 100

    # Selling price calculation
    selling_price = supplier_price / (1 - (commission_rate + promo_rate + margin_rate))

    # Cost breakdown
    commission_cost = selling_price * commission_rate
    promo_cost = selling_price * promo_rate
    total_cost = supplier_price + commission_cost + promo_cost

    # Net profit (margin)
    net_profit = selling_price - total_cost

    return round(selling_price, 2), round(net_profit, 2), round(promo_cost, 2)

def main():
    parser = argparse.ArgumentParser(
        description="CLI tool untuk menghitung harga jual, laba bersih, dan biaya ads berdasarkan harga supplier."
    )
    parser.add_argument(
        "supplier_price", 
        type=float, 
        help="Harga awal barang dari supplier (Rp)"
    )
    parser.add_argument(
        "--commission", 
        type=float, 
        default=6.0, 
        help="Persentase komisi platform (default: 6%)"
    )
    parser.add_argument(
        "--promo", 
        type=float, 
        default=8.0, 
        help="Persentase alokasi promosi/ads (default: 8%)"
    )
    parser.add_argument(
        "--margin", 
        type=float, 
        default=15.0, 
        help="Persentase margin laba bersih yang diinginkan (default: 15%)"
    )

    args = parser.parse_args()

    price, profit, ad_budget = calculate_selling_price(
        args.supplier_price,
        args.commission,
        args.promo,
        args.margin
    )

    print("\n=== Hasil Perhitungan Harga Jual ===")
    print(f"Harga Supplier          : Rp {args.supplier_price:,.2f}")
    print(f"Komisi Platform ({args.commission}%) : Rp {args.supplier_price * (args.commission/100):,.2f}")
    print(f"Budget Promosi ({args.promo}%)     : Rp {ad_budget:,.2f}")
    print(f"Margin Target ({args.margin}%)     : Rp {profit:,.2f}")
    print("-----------------------------------")
    print(f"Harga Jual yang Direkomendasikan: Rp {price:,.2f}")

if __name__ == "__main__":
    main()
