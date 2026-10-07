# Power BI dashboard guide (30-45 min)

After running `python src/analysis.py`, use the files in `results/powerbi/`.

1. **Get Data -> Text/CSV**: load `clean_orders.csv`, `category_revenue.csv`, `monthly_revenue.csv`, `late_pct_by_state.csv`.
2. In Power Query, check `month` is Text, `delay_days`/`revenue` are Decimal, `is_late` is True/False.
3. **Cards (4):** Total Orders (count of order_id), Total Revenue (sum of revenue), Avg Review (average of review_score), Late % (average of is_late, or a measure below).
4. **Visuals:**
   - Line chart: `month` vs revenue (monthly_revenue.csv)
   - Bar chart: top 10 `category` by revenue (category_revenue.csv, Top N filter)
   - Bar chart: `customer_state` vs `late_pct` (late_pct_by_state.csv)
   - Column chart: `delay_bucket` vs average `review_score` (clean_orders.csv)
5. **Slicer:** `customer_state`.
6. Optional DAX measures:
```
Late % = DIVIDE(COUNTROWS(FILTER(clean_orders, clean_orders[is_late] = TRUE())), COUNTROWS(clean_orders))
Avg Order Value = DIVIDE(SUM(clean_orders[revenue]), COUNTROWS(clean_orders))
```
7. Take a screenshot and save it as `dashboard/dashboard.png`. Save the `.pbix` there too.

No Power BI? Use the PNG charts in `results/charts/` or build pivot charts in Excel from the CSVs.
