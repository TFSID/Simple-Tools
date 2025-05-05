import pandas as pd

# Structured list of products based on the provided text
products = [
    # T-Shirts
    {"Category": "T-Shirt", "Product": "Cotton Teteron", "Color": "All", "Price (IDR)": 49000},
    {"Category": "T-Shirt", "Product": "Oversize", "Color": "Putih", "Price (IDR)": 75000},
    {"Category": "T-Shirt", "Product": "Oversize", "Color": "Selain Putih", "Price (IDR)": 85000},
    {"Category": "T-Shirt", "Product": "Oversize Boxy", "Color": "All", "Price (IDR)": 89000},
    {"Category": "T-Shirt", "Product": "Crop Top", "Color": "All", "Price (IDR)": 69000},
    {"Category": "T-Shirt", "Product": "Cotton Bamboo", "Color": "Putih", "Price (IDR)": 72000},
    {"Category": "T-Shirt", "Product": "Cotton Bamboo", "Color": "Selain Putih", "Price (IDR)": 74000},

    # Shirts - Cotton Combed
    {"Category": "Shirt", "Product": "Kaos Polo", "Color": "All", "Price (IDR)": 79000},
    {"Category": "Shirt", "Product": "Cotton Combed 20s", "Color": "Putih", "Price (IDR)": 61000},
    {"Category": "Shirt", "Product": "Cotton Combed 20s", "Color": "Selain Putih", "Price (IDR)": 69000},
    {"Category": "Shirt", "Product": "Cotton Combed 24s", "Color": "Putih", "Price (IDR)": 59500},
    {"Category": "Shirt", "Product": "Cotton Combed 24s", "Color": "Selain Putih", "Price (IDR)": 66000},
    {"Category": "Shirt", "Product": "Cotton Combed 30s", "Color": "Putih", "Price (IDR)": 57000},
    {"Category": "Shirt", "Product": "Cotton Combed 30s", "Color": "Selain Putih", "Price (IDR)": 66000},
    
    # Long Sleeve
    {"Category": "Long Sleeve", "Product": "Cotton Combed 30s", "Color": "Putih", "Price (IDR)": 65000},
    {"Category": "Long Sleeve", "Product": "Cotton Combed 30s", "Color": "Selain Putih", "Price (IDR)": 75000},
    {"Category": "Long Sleeve", "Product": "Cotton Combed 24s", "Color": "All", "Price (IDR)": 85000},
    
    # Kids
    {"Category": "Kaos Anak", "Product": "Pendek", "Color": "All", "Price (IDR)": 39000},
    {"Category": "Kaos Anak", "Product": "Panjang", "Color": "All", "Price (IDR)": 43000},

    # Hoodie/Jacket/Sweater
    {"Category": "Hoodie", "Product": "Hoodie", "Color": "All", "Price (IDR)": 119000},
    {"Category": "Hoodie", "Product": "Hoodie Anak", "Color": "All", "Price (IDR)": 79000},
    {"Category": "Hoodie", "Product": "Hoodie Boxy", "Color": "All", "Price (IDR)": 129000},
    {"Category": "Hoodie", "Product": "Hoodie Zipper", "Color": "All", "Price (IDR)": 119000},
    {"Category": "Jacket", "Product": "Sacket Jacket", "Color": "All", "Price (IDR)": 149000},
    {"Category": "Jacket", "Product": "Coach Jacket", "Color": "All", "Price (IDR)": 127000},
    {"Category": "Sweater", "Product": "Crewneck", "Color": "Putih", "Price (IDR)": 89000},
    {"Category": "Sweater", "Product": "Crewneck", "Color": "Selain Putih", "Price (IDR)": 99000},

    # Accessories
    {"Category": "Accessories", "Product": "Topi Baseball", "Color": "All", "Price (IDR)": 35000},
    {"Category": "Accessories", "Product": "Totebag Canvas", "Color": "All", "Price (IDR)": 25000},
    {"Category": "Accessories", "Product": "Totebag Canvas Resleting", "Color": "All", "Price (IDR)": 27000},
    {"Category": "Accessories", "Product": "Totebag Fullprint", "Color": "All", "Price (IDR)": 89000},
    {"Category": "Accessories", "Product": "Backpack Custom", "Color": "All", "Price (IDR)": 75000},
    {"Category": "Accessories", "Product": "Sling Bag", "Color": "All", "Price (IDR)": 59000},
]

# Create DataFrame
df = pd.DataFrame(products)

# Save as Excel and CSV
excel_path = "zenvia_product_list.xlsx"
csv_path = "zenvia_product_list.csv"
df.to_excel(excel_path, index=False)
df.to_csv(csv_path, index=False)

excel_path, csv_path
