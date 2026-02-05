"""
build_system.py
Builds SQLite DB from CSVs (raw_store) and schema (database)
"""
import os
import sqlite3
import pandas as pd

BASE = os.path.join(os.path.dirname(__file__), "..")
DB_DIR = os.path.join(BASE, "database")
RAW = os.path.join(BASE, "raw_store")
DB_PATH = os.path.join(RAW, "telecom_store.db")

SCHEMA_PATH = os.path.join(DB_DIR, "store_schema.sql")

def main():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON;")

    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())

    load_order = ["customers","reps","plans","products","inventory","sales","sale_items","returns"]
    for table in load_order:
        csv_path = os.path.join(RAW, f"{table}.csv")
        df = pd.read_csv(csv_path)
        df.to_sql(table, conn, if_exists="append", index=False)

    conn.commit()
    conn.close()
    print(f"Database created: {DB_PATH}")

if __name__ == "__main__":
    main()
