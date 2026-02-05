"""
performance_report.py
Creates KPI summary + charts in insights/
"""
import os
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt

BASE = os.path.join(os.path.dirname(__file__), "..")
RAW = os.path.join(BASE, "raw_store")
OUT = os.path.join(BASE, "insights")
os.makedirs(OUT, exist_ok=True)

DB_PATH = os.path.join(RAW, "telecom_store.db")

def main():
    conn = sqlite3.connect(DB_PATH)

    # Revenue by day (exclude returned items)
    revenue_day_sql = """
    WITH returned AS (SELECT sale_item_id FROM returns),
    net_items AS (
      SELECT s.sale_datetime, si.*
      FROM sales s
      JOIN sale_items si ON si.sale_id = s.sale_id
      LEFT JOIN returned r ON r.sale_item_id = si.sale_item_id
      WHERE r.sale_item_id IS NULL
    )
    SELECT date(sale_datetime) AS sale_date,
           SUM((unit_price * quantity) - discount_amount) AS net_revenue
    FROM net_items
    GROUP BY date(sale_datetime)
    ORDER BY sale_date;
    """
    revenue_day = pd.read_sql_query(revenue_day_sql, conn)

    # Revenue by rep
    revenue_rep_sql = """
    WITH returned AS (SELECT sale_item_id FROM returns),
    net_items AS (
      SELECT s.rep_id, si.*
      FROM sales s
      JOIN sale_items si ON si.sale_id = s.sale_id
      LEFT JOIN returned r ON r.sale_item_id = si.sale_item_id
      WHERE r.sale_item_id IS NULL
    )
    SELECT r.rep_name,
           SUM((unit_price * quantity) - discount_amount) AS net_revenue
    FROM net_items
    JOIN reps r ON r.rep_id = net_items.rep_id
    GROUP BY r.rep_id
    ORDER BY net_revenue DESC;
    """
    revenue_rep = pd.read_sql_query(revenue_rep_sql, conn)

    # Attach rate (upsell)
    attach_sql = """
    WITH returned AS (SELECT sale_item_id FROM returns),
    net_sale_items AS (
      SELECT si.sale_id, si.sale_item_id, si.item_type, si.product_id, si.quantity
      FROM sale_items si
      LEFT JOIN returned r ON r.sale_item_id = si.sale_item_id
      WHERE r.sale_item_id IS NULL
    ),
    devices AS (
      SELECT SUM(nsi.quantity) AS device_qty
      FROM net_sale_items nsi
      JOIN products p ON p.product_id = nsi.product_id
      WHERE nsi.item_type='Product' AND p.category='Device'
    ),
    accessories AS (
      SELECT SUM(nsi.quantity) AS acc_qty
      FROM net_sale_items nsi
      JOIN products p ON p.product_id = nsi.product_id
      WHERE nsi.item_type='Product' AND p.category IN ('Accessory','Protection')
    )
    SELECT COALESCE(acc_qty,0) * 1.0 / NULLIF(device_qty,0) AS attach_rate
    FROM devices, accessories;
    """
    attach_rate = float(pd.read_sql_query(attach_sql, conn).iloc[0, 0])

    # AOV
    aov_sql = """
    WITH returned AS (SELECT sale_item_id FROM returns),
    sale_totals AS (
      SELECT s.sale_id,
             SUM((si.unit_price * si.quantity) - si.discount_amount) AS sale_total
      FROM sales s
      JOIN sale_items si ON si.sale_id = s.sale_id
      LEFT JOIN returned r ON r.sale_item_id = si.sale_item_id
      WHERE r.sale_item_id IS NULL
      GROUP BY s.sale_id
    )
    SELECT AVG(sale_total) AS aov
    FROM sale_totals;
    """
    aov = float(pd.read_sql_query(aov_sql, conn).iloc[0, 0])

    total_rev = float(revenue_day["net_revenue"].sum())
    est_commission = total_rev * 0.02  # example logic

    summary = pd.DataFrame([
        {"metric": "Total Net Revenue", "value": round(total_rev, 2)},
        {"metric": "Average Order Value (AOV)", "value": round(aov, 2)},
        {"metric": "Accessory Attach Rate", "value": round(attach_rate, 2)},
        {"metric": "Est. Commission (2% example)", "value": round(est_commission, 2)},
    ])
    summary.to_csv(os.path.join(OUT, "kpi_summary.csv"), index=False)

    # Charts
    plt.figure()
    plt.plot(pd.to_datetime(revenue_day["sale_date"]), revenue_day["net_revenue"])
    plt.xticks(rotation=45, ha="right")
    plt.title("Net Revenue by Day")
    plt.xlabel("Date")
    plt.ylabel("Net Revenue")
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "revenue_by_day.png"))
    plt.close()

    plt.figure()
    plt.bar(revenue_rep["rep_name"], revenue_rep["net_revenue"])
    plt.title("Net Revenue by Rep")
    plt.xlabel("Rep")
    plt.ylabel("Net Revenue")
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "revenue_by_rep.png"))
    plt.close()

    plt.figure()
    plt.bar(["Attach Rate"], [attach_rate])
    plt.title("Accessory Attach Rate (Upsell)")
    plt.ylabel("Accessories per Device")
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "attach_rate.png"))
    plt.close()

    conn.close()
    print("Insights generated in insights/")

if __name__ == "__main__":
    main()
