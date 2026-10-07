"""
Olist E-commerce Analysis: Sales, Delivery Delays and Customer Reviews.

Reads the raw Olist CSVs from ./data, cleans them, computes all metrics,
saves tables, charts, Power BI-ready CSVs and an auto-generated results/FINDINGS.md.

Run from the project root:  python src/analysis.py
"""
from pathlib import Path
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
TABLES = ROOT / "results" / "tables"
CHARTS = ROOT / "results" / "charts"
POWERBI = ROOT / "results" / "powerbi"
for p in (TABLES, CHARTS, POWERBI):
    p.mkdir(parents=True, exist_ok=True)

PINK, BLUE = "#d6336c", "#364fc7"


def load():
    needed = {
        "orders": "olist_orders_dataset.csv",
        "items": "olist_order_items_dataset.csv",
        "reviews": "olist_order_reviews_dataset.csv",
        "payments": "olist_order_payments_dataset.csv",
        "customers": "olist_customers_dataset.csv",
        "products": "olist_products_dataset.csv",
        "trans": "product_category_name_translation.csv",
    }
    missing = [f for f in needed.values() if not (DATA / f).exists()]
    if missing:
        sys.exit(f"Missing files in data/: {missing}\nSee data/README.md")
    date_cols = [
        "order_purchase_timestamp", "order_approved_at",
        "order_delivered_carrier_date", "order_delivered_customer_date",
        "order_estimated_delivery_date",
    ]
    d = {k: pd.read_csv(DATA / v) for k, v in needed.items()}
    for c in date_cols:
        d["orders"][c] = pd.to_datetime(d["orders"][c], errors="coerce")
    return d


def main():
    d = load()
    log = {}  # data-cleaning notes

    orders = d["orders"]
    log["total_orders_raw"] = len(orders)
    log["status_counts"] = orders["order_status"].value_counts().to_dict()

    # ---------- Cleaning ----------
    delivered = orders[orders["order_status"] == "delivered"].copy()
    log["delivered_orders"] = len(delivered)
    log["delivered_missing_delivery_date"] = int(delivered["order_delivered_customer_date"].isna().sum())
    delivered = delivered.dropna(subset=["order_delivered_customer_date"])

    # Some orders have multiple reviews -> average per order
    log["orders_with_multiple_reviews"] = int((d["reviews"].groupby("order_id").size() > 1).sum())
    review_per_order = (d["reviews"].groupby("order_id")["review_score"]
                        .mean().rename("review_score").reset_index())

    cust = d["customers"][["customer_id", "customer_unique_id", "customer_state"]]
    delivered = (delivered.merge(cust, on="customer_id", how="left")
                          .merge(review_per_order, on="order_id", how="left"))

    delivered["delay_days"] = (delivered["order_delivered_customer_date"]
                               - delivered["order_estimated_delivery_date"]).dt.total_seconds() / 86400
    delivered["is_late"] = delivered["delay_days"] > 0
    delivered["month"] = delivered["order_purchase_timestamp"].dt.to_period("M").astype(str)
    delivered["delivery_days"] = (delivered["order_delivered_customer_date"]
                                  - delivered["order_purchase_timestamp"]).dt.total_seconds() / 86400

    # Items -> revenue per order (delivered only)
    items = d["items"][d["items"]["order_id"].isin(delivered["order_id"])].copy()
    rev = items.groupby("order_id").agg(revenue=("price", "sum"), freight=("freight_value", "sum")).reset_index()
    delivered = delivered.merge(rev, on="order_id", how="left")
    delivered[["revenue", "freight"]] = delivered[["revenue", "freight"]].fillna(0)

    # ---------- A. Sales ----------
    total_revenue = delivered["revenue"].sum()
    n_orders = len(delivered)
    aov = total_revenue / n_orders

    monthly = (delivered.groupby("month")
               .agg(orders=("order_id", "nunique"), revenue=("revenue", "sum")).reset_index())
    monthly = monthly[monthly["orders"] >= 100]  # drop near-empty start/end months
    monthly.to_csv(TABLES / "monthly_revenue.csv", index=False)

    prod = d["products"].merge(d["trans"], on="product_category_name", how="left")
    prod["category"] = prod["product_category_name_english"].fillna(prod["product_category_name"]).fillna("unknown")
    items = items.merge(prod[["product_id", "category"]], on="product_id", how="left")
    items = items.merge(review_per_order, on="order_id", how="left")

    cat_rev = (items.groupby("category")
               .agg(revenue=("price", "sum"), items_sold=("order_item_id", "count")).reset_index()
               .sort_values("revenue", ascending=False))
    cat_rev.to_csv(TABLES / "category_revenue.csv", index=False)
    top_cat = cat_rev.head(10)

    pay = d["payments"]["payment_type"].value_counts(normalize=True).mul(100).round(1)
    pay = pay[pay.index != "not_defined"].rename("pct").reset_index()
    pay.columns = ["payment_type", "pct"]
    pay.to_csv(TABLES / "payment_share.csv", index=False)

    # ---------- B. Delivery ----------
    late_pct = delivered["is_late"].mean() * 100
    by_status = (delivered.dropna(subset=["review_score"])
                 .groupby("is_late")["review_score"].mean())
    avg_review = delivered["review_score"].mean()
    rev_on_time = by_status.get(False, np.nan)
    rev_late = by_status.get(True, np.nan)

    # Buckets: early (<0), on time (0), 1-3 late, 4-7 late, 7+ late (days rounded up)
    days = np.ceil(delivered["delay_days"])
    delivered["delay_bucket"] = pd.cut(
        days, bins=[-np.inf, -1, 0, 3, 7, np.inf],
        labels=["Early", "On time", "1-3 days late", "4-7 days late", "7+ days late"])
    bucket = (delivered.groupby("delay_bucket", observed=True)
              .agg(orders=("order_id", "count"), avg_review=("review_score", "mean")).reset_index())
    bucket.to_csv(TABLES / "review_by_delay_bucket.csv", index=False)

    state = (delivered.groupby("customer_state")
             .agg(orders=("order_id", "count"), late_pct=("is_late", lambda s: s.mean() * 100),
                  avg_review=("review_score", "mean"), avg_delivery_days=("delivery_days", "mean"))
             .reset_index())
    min_state_orders = 500 if len(delivered) > 20000 else 1
    state = state[state["orders"] >= min_state_orders].sort_values("late_pct", ascending=False)
    state.to_csv(TABLES / "late_pct_by_state.csv", index=False)

    # ---------- C. Satisfaction & retention ----------
    low_cat = (items.dropna(subset=["review_score"]).groupby("category")
               .agg(reviews=("review_score", "count"), avg_review=("review_score", "mean")).reset_index())
    min_reviews = 200 if len(delivered) > 20000 else 1
    low_cat = low_cat[low_cat["reviews"] >= min_reviews].sort_values("avg_review").head(10)
    low_cat.to_csv(TABLES / "lowest_rated_categories.csv", index=False)

    per_cust = delivered.groupby("customer_unique_id")["order_id"].nunique()
    repeat_pct = (per_cust > 1).mean() * 100

    # ---------- Charts ----------
    def style(ax):
        ax.spines[["top", "right"]].set_visible(False)

    fig, ax = plt.subplots(figsize=(10, 4.5))
    ax.plot(monthly["month"], monthly["revenue"], color=PINK, marker="o")
    ax.set_title("Monthly Revenue (delivered orders)")
    ax.set_ylabel("Revenue (BRL)")
    ax.tick_params(axis="x", rotation=60)
    style(ax)
    fig.tight_layout(); fig.savefig(CHARTS / "01_monthly_revenue.png", dpi=150); plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 5))
    top_cat.iloc[::-1].plot(kind="barh", x="category", y="revenue", ax=ax, color=BLUE, legend=False)
    ax.set_title("Top 10 Categories by Revenue"); ax.set_xlabel("Revenue (BRL)"); ax.set_ylabel("")
    style(ax)
    fig.tight_layout(); fig.savefig(CHARTS / "02_top_categories.png", dpi=150); plt.close(fig)

    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.bar(bucket["delay_bucket"].astype(str), bucket["avg_review"], color=PINK)
    ax.set_title("Average Review Score by Delivery Delay"); ax.set_ylabel("Avg review (1-5)")
    ax.set_ylim(0, 5); ax.tick_params(axis="x", rotation=25)
    style(ax)
    fig.tight_layout(); fig.savefig(CHARTS / "03_review_vs_delay.png", dpi=150); plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 4.5))
    top_state = state.head(10)
    ax.bar(top_state["customer_state"], top_state["late_pct"], color=BLUE)
    ax.set_title("Top 10 States by Late Delivery %"); ax.set_ylabel("% orders late")
    style(ax)
    fig.tight_layout(); fig.savefig(CHARTS / "04_late_by_state.png", dpi=150); plt.close(fig)

    fig, ax = plt.subplots(figsize=(9, 5))
    low_cat.iloc[::-1].plot(kind="barh", x="category", y="avg_review", ax=ax, color=PINK, legend=False)
    ax.set_title("Lowest-Rated Categories"); ax.set_xlabel("Avg review"); ax.set_ylabel("")
    style(ax)
    fig.tight_layout(); fig.savefig(CHARTS / "05_lowest_rated_categories.png", dpi=150); plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 4))
    ax.bar(pay["payment_type"], pay["pct"], color=BLUE)
    ax.set_title("Payment Method Share (%)")
    style(ax)
    fig.tight_layout(); fig.savefig(CHARTS / "06_payment_share.png", dpi=150); plt.close(fig)

    # ---------- Power BI export ----------
    delivered[["order_id", "customer_unique_id", "customer_state", "month", "revenue", "freight",
               "review_score", "delay_days", "delay_bucket", "is_late", "delivery_days"]
              ].to_csv(POWERBI / "clean_orders.csv", index=False)
    cat_rev.to_csv(POWERBI / "category_revenue.csv", index=False)
    monthly.to_csv(POWERBI / "monthly_revenue.csv", index=False)
    state.to_csv(POWERBI / "late_pct_by_state.csv", index=False)

    # ---------- FINDINGS.md ----------
    worst = state.head(3)
    best = state.iloc[-1]
    pay_lines = "\n".join(f"- {r.payment_type}: {r.pct}%" for r in pay.itertuples())
    states_txt = ", ".join(f"{r.customer_state} ({r.late_pct:.1f}%)" for r in worst.itertuples())
    md = f"""# Findings (auto-generated from your data)

## Data cleaning notes
- Raw orders: **{log['total_orders_raw']:,}**; status breakdown: {log['status_counts']}
- Analysed only `delivered` orders: **{log['delivered_orders']:,}**
- Delivered orders with no delivery date (excluded): **{log['delivered_missing_delivery_date']}**
- Orders with more than one review (score averaged per order): **{log['orders_with_multiple_reviews']:,}**
- Months with fewer than 100 orders are dropped from the trend chart (partial start/end months)

## Headline KPIs
| KPI | Value |
|---|---|
| Orders analysed | {n_orders:,} |
| Total revenue (item price) | {total_revenue:,.0f} BRL |
| Average order value | {aov:,.2f} BRL |
| Average review score | {avg_review:.2f} / 5 |
| Late delivery rate | {late_pct:.1f}% |
| Repeat customer rate | {repeat_pct:.1f}% |

## Key insights
1. **Late deliveries hurt reviews:** on-time orders average **{rev_on_time:.2f}** vs **{rev_late:.2f}** for late orders.
2. **Delay severity matters:** average review goes from **{bucket['avg_review'].iloc[0]:.2f}** ({bucket['delay_bucket'].iloc[0]}) to **{bucket['avg_review'].iloc[-1]:.2f}** ({bucket['delay_bucket'].iloc[-1]}).
3. **Worst states for late delivery:** {states_txt}; best: {best['customer_state']} ({best['late_pct']:.1f}%).
4. **Top revenue category:** {top_cat.iloc[0]['category']} ({top_cat.iloc[0]['revenue']:,.0f} BRL); the top 3 categories make up {top_cat.head(3)['revenue'].sum() / total_revenue * 100:.1f}% of revenue.
5. **Lowest-rated category (200+ reviews):** {low_cat.iloc[0]['category']} ({low_cat.iloc[0]['avg_review']:.2f}).
6. **Repeat purchases:** **{repeat_pct:.1f}%** of customers ordered more than once.

## Recommendations (rewrite in your own words)
- Prioritise logistics fixes in the highest-late-rate states and set more realistic delivery estimates there.
- Proactively contact customers whose orders are running late, since review scores drop with delay.
- Investigate quality issues in the lowest-rated categories.
- Use post-delivery offers or follow-ups to lift the repeat purchase rate.

## Payment mix (% of payments)
{pay_lines}
"""
    (ROOT / "results" / "FINDINGS.md").write_text(md)
    print(md)
    print("\nDone. See results/ for charts, tables, Power BI files and FINDINGS.md")


if __name__ == "__main__":
    main()
