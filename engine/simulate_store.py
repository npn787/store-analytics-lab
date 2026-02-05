"""
simulate_store.py
Generates realistic synthetic data as CSVs into ../raw_store
"""
import os
import random
from datetime import datetime, timedelta
import pandas as pd

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "raw_store")
os.makedirs(OUT_DIR, exist_ok=True)

random.seed(7)

CITIES = ["Regina", "Saskatoon", "Moose Jaw", "Prince Albert", "Swift Current", "Yorkton"]
SEGMENTS = ["Student", "Family", "Business", "Senior", "General"]

def make_customers(n=250):
    first = ["Neel","Aman","Raj","Simran","Kiran","Arjun","Priya","Riya","Sara","Noah","Liam","Olivia","Emma","Maya","Ishaan"]
    last = ["Patel","Singh","Kaur","Sharma","Gupta","Brown","Smith","Johnson","Williams","Davis","Miller"]
    rows = []
    base_date = datetime.now() - timedelta(days=180)

    for i in range(1, n + 1):
        fn = random.choice(first)
        ln = random.choice(last)
        city = random.choice(CITIES)
        seg = random.choices(SEGMENTS, weights=[18, 28, 12, 10, 32])[0]
        created = base_date + timedelta(days=random.randint(0, 180))
        rows.append([i, fn, ln, city, seg, created.isoformat(timespec="seconds")])

    return pd.DataFrame(rows, columns=["customer_id","first_name","last_name","city","segment","created_at"])

def make_reps():
    reps = [
        (1, "Samar", "Regina"),
        (2, "Avery", "Regina"),
        (3, "Devon", "Regina"),
        (4, "Kai", "Regina"),
    ]
    return pd.DataFrame(reps, columns=["rep_id","rep_name","store_city"])

def make_plans():
    plans = [
        (1, "Saver 10GB", "Postpaid", 10, 45.0),
        (2, "Everyday 30GB", "Postpaid", 30, 65.0),
        (3, "Unlimited 60GB", "Postpaid", 60, 80.0),
        (4, "Prepaid 5GB", "Prepaid", 5, 30.0),
        (5, "Business Pro 100GB", "Business", 100, 120.0),
    ]
    return pd.DataFrame(plans, columns=["plan_id","plan_name","plan_type","data_gb","monthly_price"])

def make_products():
    products = [
        ("DEV-APL-014", "iPhone 14", "Device", "Apple", 650, 899),
        ("DEV-APL-015", "iPhone 15", "Device", "Apple", 780, 1099),
        ("DEV-SAM-S23", "Galaxy S23", "Device", "Samsung", 700, 999),
        ("DEV-GOO-P08", "Pixel 8", "Device", "Google", 620, 899),
        ("ACC-CASE-PR", "Protective Case", "Accessory", "Generic", 8, 29),
        ("ACC-GLASS", "Screen Protector", "Accessory", "Generic", 2, 15),
        ("ACC-CHRG-25", "Fast Charger 25W", "Accessory", "Generic", 10, 35),
        ("PROT-PLUS", "Device Protection", "Protection", "Coverage", 0, 12),
        ("ACC-EARB-WL", "Wireless Earbuds", "Accessory", "Generic", 18, 59),
    ]
    rows = []
    pid = 1
    for sku, name, cat, brand, cost, price in products:
        rows.append([pid, sku, name, cat, brand, float(cost), float(price)])
        pid += 1
    return pd.DataFrame(rows, columns=["product_id","sku","product_name","category","brand","unit_cost","unit_price"])

def make_inventory(products_df):
    rows = []
    for _, r in products_df.iterrows():
        stock = random.randint(5, 60) if r["category"] != "Device" else random.randint(2, 25)
        reorder = 10 if r["category"] != "Device" else 5
        rows.append([int(r["product_id"]), int(stock), int(reorder)])
    return pd.DataFrame(rows, columns=["product_id","stock_on_hand","reorder_level"])

def make_sales(customers_df, reps_df, plans_df, products_df, days=60, sales_per_day=(6, 16)):
    sales_rows = []
    item_rows = []
    return_rows = []

    sale_id = 1
    sale_item_id = 1

    start = datetime.now() - timedelta(days=days)
    reps = reps_df["rep_id"].tolist()
    customers = customers_df["customer_id"].tolist()
    plan_ids = plans_df["plan_id"].tolist()
    device_ids = products_df[products_df["category"]=="Device"]["product_id"].tolist()
    accessory_ids = products_df[products_df["category"].isin(["Accessory","Protection"])]["product_id"].tolist()

    for d in range(days):
        day = start + timedelta(days=d)
        count = random.randint(*sales_per_day)

        for _ in range(count):
            dt = day + timedelta(minutes=random.randint(0, 60*10))
            rep_id = random.choice(reps)
            cust_id = random.choice(customers)
            channel = random.choices(["InStore","Phone","Email"], weights=[78, 12, 10])[0]
            sales_rows.append([sale_id, dt.isoformat(timespec="seconds"), rep_id, cust_id, channel])

            def add_product(pid, qty=1, discount=0.0):
                nonlocal sale_item_id
                price = float(products_df.loc[products_df["product_id"]==pid, "unit_price"].iloc[0])
                item_rows.append([sale_item_id, sale_id, "Product", None, int(pid), int(qty), price, float(discount)])

                # 6% return chance for in-store products (realistic)
                if random.random() < 0.06 and channel == "InStore":
                    reason = random.choice(["Changed mind","Defective","Wrong fit","Better deal elsewhere"])
                    rdt = dt + timedelta(days=random.randint(1, 14))
                    return_rows.append([None, sale_item_id, rdt.isoformat(timespec="seconds"), reason])

                sale_item_id += 1

            def add_plan(pid):
                nonlocal sale_item_id
                price = float(plans_df.loc[plans_df["plan_id"]==pid, "monthly_price"].iloc[0])
                item_rows.append([sale_item_id, sale_id, "Plan", int(pid), None, 1, price, 0.0])
                sale_item_id += 1

            roll = random.random()

            # Most common: device + plan + accessories
            if roll < 0.70:
                dev = random.choice(device_ids)
                plan = random.choice(plan_ids)
                dev_disc = random.choice([0, 0, 0, 20, 30, 40, 50])  # occasional promo discount
                add_product(dev, qty=1, discount=dev_disc)
                add_plan(plan)

                acc_count = random.choices([0,1,2,3], weights=[25, 40, 25, 10])[0]
                for _a in range(acc_count):
                    add_product(random.choice(accessory_ids), qty=1)

            # Plan-only
            elif roll < 0.90:
                add_plan(random.choice(plan_ids))
                if random.random() < 0.35:
                    add_product(random.choice(accessory_ids), qty=1)

            # Accessory-only
            else:
                add_product(random.choice(accessory_ids), qty=1)

            sale_id += 1

    sales_df = pd.DataFrame(sales_rows, columns=["sale_id","sale_datetime","rep_id","customer_id","channel"])
    items_df = pd.DataFrame(item_rows, columns=["sale_item_id","sale_id","item_type","plan_id","product_id","quantity","unit_price","discount_amount"])
    returns_df = pd.DataFrame(return_rows, columns=["return_id","sale_item_id","return_datetime","reason"])

    return sales_df, items_df, returns_df

def main():
    customers = make_customers()
    reps = make_reps()
    plans = make_plans()
    products = make_products()
    inventory = make_inventory(products)
    sales, items, returns = make_sales(customers, reps, plans, products, days=60)

    customers.to_csv(os.path.join(OUT_DIR, "customers.csv"), index=False)
    reps.to_csv(os.path.join(OUT_DIR, "reps.csv"), index=False)
    plans.to_csv(os.path.join(OUT_DIR, "plans.csv"), index=False)
    products.to_csv(os.path.join(OUT_DIR, "products.csv"), index=False)
    inventory.to_csv(os.path.join(OUT_DIR, "inventory.csv"), index=False)
    sales.to_csv(os.path.join(OUT_DIR, "sales.csv"), index=False)
    items.to_csv(os.path.join(OUT_DIR, "sale_items.csv"), index=False)
    returns.to_csv(os.path.join(OUT_DIR, "returns.csv"), index=False)

    print("Store simulation generated CSVs in raw_store/")

if __name__ == "__main__":
    main()