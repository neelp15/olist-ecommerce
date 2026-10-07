"""
Load the Olist CSVs into a MySQL database called `olist` so you can run the SQL files.

1. In MySQL Workbench run:  CREATE DATABASE olist;
2. Edit PASSWORD below.
3. Run from the project root:  python src/load_to_mysql.py
"""
from pathlib import Path
import pandas as pd
from sqlalchemy import create_engine

USER, PASSWORD, HOST, DB = "root", "150304", "localhost", "olist"
DATA = Path(__file__).resolve().parent.parent / "data"

engine = create_engine(f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}/{DB}")

files = {
    "orders": "olist_orders_dataset.csv",
    "order_items": "olist_order_items_dataset.csv",
    "order_reviews": "olist_order_reviews_dataset.csv",
    "order_payments": "olist_order_payments_dataset.csv",
    "customers": "olist_customers_dataset.csv",
    "products": "olist_products_dataset.csv",
    "category_translation": "product_category_name_translation.csv",
}
date_cols = {
    "orders": ["order_purchase_timestamp", "order_approved_at", "order_delivered_carrier_date",
               "order_delivered_customer_date", "order_estimated_delivery_date"],
    "order_items": ["shipping_limit_date"],
    "order_reviews": ["review_creation_date", "review_answer_timestamp"],
}

for table, file in files.items():
    df = pd.read_csv(DATA / file, parse_dates=date_cols.get(table, []))
    if table == "order_reviews":  # long free text, not needed
        df = df.drop(columns=["review_comment_title", "review_comment_message"], errors="ignore")
    df.to_sql(table, engine, if_exists="replace", index=False, chunksize=10000)
    print(f"{table}: {len(df):,} rows loaded")
