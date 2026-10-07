# Resume entry and interview prep

## Resume bullets (replace the blanks with numbers from results/FINDINGS.md)

**E-commerce Sales, Delivery & Review Analysis | SQL (MySQL), Python, Pandas, Power BI**  [GitHub link]
- Analyzed ~96k delivered orders across 7 relational tables using SQL JOINs, CTEs and window functions.
- Cleaned the data (excluded orders with missing delivery dates, averaged duplicate reviews per order) and built KPIs for revenue, AOV, late-delivery rate and repeat purchases.
- Found that late orders averaged __ stars vs __ for on-time orders, and that __ states had the highest late-delivery rates.
- Built an interactive dashboard and recommended logistics and customer-communication improvements.

Use only numbers you actually computed.

## 60-second explanation
"I analysed the Olist e-commerce dataset, about 100k orders, to understand how delivery performance affects customer satisfaction. I loaded the data into MySQL, cleaned it, and wrote SQL queries with joins and window functions, then used Python for charts and Power BI for a dashboard. I found that [late orders get __ vs __ stars], and that [states] have the highest delays. I recommended [fix]. Since a Product Analyst works on customer issues, this showed me how data can point to the root cause of unhappy customers."

## Likely questions
- **Why only delivered orders?** Other statuses have no delivery outcome or review to compare.
- **Why LEFT JOIN on the category translation table?** To keep products whose category has no English translation.
- **How did you handle duplicate reviews / null dates?** Averaged review per order; excluded delivered orders with no delivery date (state the count).
- **INNER vs LEFT JOIN?** INNER keeps matches only; LEFT keeps all rows from the left table.
- **WHERE vs HAVING?** WHERE filters rows before grouping; HAVING filters groups after aggregation.
- **What does RANK() OVER (PARTITION BY ...) do?** Ranks rows within each group without collapsing them.
- **Correlation vs causation?** Late delivery is associated with lower reviews, but other factors (product quality, price) may also play a part.
- **Why this project for a Product Analyst/support role?** It deals with customer pain points: finding what drives unhappy customers and recommending fixes.

## SQL to practise tonight
JOIN types, GROUP BY + HAVING, CASE WHEN, subqueries, CTEs, RANK/ROW_NUMBER, DATE functions, COUNT(DISTINCT), NULL handling.
