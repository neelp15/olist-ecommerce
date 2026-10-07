# Olist E-commerce Analysis: Sales, Delivery Delays & Customer Reviews

End-to-end analytics project on the Brazilian Olist e-commerce dataset (~100k orders, 7 relational tables).

## Business problem
Do late deliveries hurt customer reviews? Which regions and product categories need attention,
and where does the revenue come from?

## Tools
MySQL (JOINs, CTEs, window functions) · Python (Pandas, Matplotlib) · Power BI / Excel

## Dataset
[Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce) (Kaggle).
Place the CSVs in `data/` (see `data/README.md`).

## Key findings
> Copy your real numbers from `results/FINDINGS.md` after running the analysis.

- **Late deliveries:** X% of orders arrived late; late orders average __ stars vs __ for on-time orders.
- **Regions:** the worst states for late delivery are __, __, __.
- **Sales:** __ is the top category by revenue; the top 3 categories make up __% of revenue.
- **Retention:** only __% of customers purchased more than once.

## Recommendations
1. Improve logistics and delivery estimates in the highest-delay states.
2. Proactively communicate with customers whose orders are delayed.
3. Investigate quality issues in the lowest-rated categories.
4. Introduce follow-up offers to improve repeat purchases.

## Project structure
```
data/        raw CSVs (git-ignored)
sql/         00 data quality checks, 01 sales, 02 delivery, 03 customers
src/         load_to_mysql.py, analysis.py
results/     charts/, tables/, powerbi/, FINDINGS.md   (generated)
dashboard/   your Power BI screenshot / .pbix
docs/        resume and interview guide
```

## How to run
```bash
pip install -r requirements.txt

# Option A: Python only (no database needed). Generates charts, tables, Power BI files and FINDINGS.md
python src/analysis.py

# Option B: SQL analysis in MySQL
#   1. In MySQL Workbench: CREATE DATABASE olist;
#   2. Set your password in src/load_to_mysql.py
python src/load_to_mysql.py
#   3. Open and run the files in sql/ in order
```

## Dashboard
![Dashboard](dashboard/dashboard.png)
