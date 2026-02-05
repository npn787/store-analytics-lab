PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS customers (
  customer_id INTEGER PRIMARY KEY,
  first_name TEXT NOT NULL,
  last_name  TEXT NOT NULL,
  city       TEXT NOT NULL,
  segment    TEXT NOT NULL CHECK(segment IN ('Student','Family','Business','Senior','General')),
  created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS reps (
  rep_id   INTEGER PRIMARY KEY,
  rep_name TEXT NOT NULL,
  store_city TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS plans (
  plan_id INTEGER PRIMARY KEY,
  plan_name TEXT NOT NULL,
  plan_type TEXT NOT NULL CHECK(plan_type IN ('Prepaid','Postpaid','Business')),
  data_gb INTEGER NOT NULL,
  monthly_price REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS products (
  product_id INTEGER PRIMARY KEY,
  sku TEXT NOT NULL UNIQUE,
  product_name TEXT NOT NULL,
  category TEXT NOT NULL CHECK(category IN ('Device','Accessory','Protection')),
  brand TEXT NOT NULL,
  unit_cost REAL NOT NULL,
  unit_price REAL NOT NULL
);

CREATE TABLE IF NOT EXISTS inventory (
  product_id INTEGER PRIMARY KEY,
  stock_on_hand INTEGER NOT NULL,
  reorder_level INTEGER NOT NULL,
  FOREIGN KEY(product_id) REFERENCES products(product_id)
);

CREATE TABLE IF NOT EXISTS sales (
  sale_id INTEGER PRIMARY KEY,
  sale_datetime TEXT NOT NULL,
  rep_id INTEGER NOT NULL,
  customer_id INTEGER NOT NULL,
  channel TEXT NOT NULL CHECK(channel IN ('InStore','Phone','Email')),
  FOREIGN KEY(rep_id) REFERENCES reps(rep_id),
  FOREIGN KEY(customer_id) REFERENCES customers(customer_id)
);

CREATE TABLE IF NOT EXISTS sale_items (
  sale_item_id INTEGER PRIMARY KEY,
  sale_id INTEGER NOT NULL,
  item_type TEXT NOT NULL CHECK(item_type IN ('Plan','Product')),
  plan_id INTEGER,
  product_id INTEGER,
  quantity INTEGER NOT NULL DEFAULT 1,
  unit_price REAL NOT NULL,
  discount_amount REAL NOT NULL DEFAULT 0,
  FOREIGN KEY(sale_id) REFERENCES sales(sale_id),
  FOREIGN KEY(plan_id) REFERENCES plans(plan_id),
  FOREIGN KEY(product_id) REFERENCES products(product_id)
);

CREATE TABLE IF NOT EXISTS returns (
  return_id INTEGER PRIMARY KEY,
  sale_item_id INTEGER NOT NULL,
  return_datetime TEXT NOT NULL,
  reason TEXT NOT NULL,
  FOREIGN KEY(sale_item_id) REFERENCES sale_items(sale_item_id)
);