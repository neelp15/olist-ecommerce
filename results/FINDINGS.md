# Findings (auto-generated from your data)

## Data cleaning notes
- Raw orders: **99,441**; status breakdown: {'delivered': 96478, 'shipped': 1107, 'canceled': 625, 'unavailable': 609, 'invoiced': 314, 'processing': 301, 'created': 5, 'approved': 2}
- Analysed only `delivered` orders: **96,478**
- Delivered orders with no delivery date (excluded): **8**
- Orders with more than one review (score averaged per order): **547**
- Months with fewer than 100 orders are dropped from the trend chart (partial start/end months)

## Headline KPIs
| KPI | Value |
|---|---|
| Orders analysed | 96,470 |
| Total revenue (item price) | 13,220,249 BRL |
| Average order value | 137.04 BRL |
| Average review score | 4.16 / 5 |
| Late delivery rate | 8.1% |
| Repeat customer rate | 3.0% |

## Key insights
1. **Late deliveries hurt reviews:** on-time orders average **4.29** vs **2.57** for late orders.
2. **Delay severity matters:** average review goes from **4.30** (Early) to **1.73** (7+ days late).
3. **Worst states for late delivery:** MA (19.7%), CE (15.3%), BA (14.0%); best: PR (5.0%).
4. **Top revenue category:** health_beauty (1,233,132 BRL); the top 3 categories make up 25.9% of revenue.
5. **Lowest-rated category (200+ reviews):** office_furniture (3.51).
6. **Repeat purchases:** **3.0%** of customers ordered more than once.

## Recommendations (rewrite in your own words)
- Prioritise logistics fixes in the highest-late-rate states and set more realistic delivery estimates there.
- Proactively contact customers whose orders are running late, since review scores drop with delay.
- Investigate quality issues in the lowest-rated categories.
- Use post-delivery offers or follow-ups to lift the repeat purchase rate.

## Payment mix (% of payments)
- credit_card: 73.9%
- boleto: 19.0%
- voucher: 5.6%
- debit_card: 1.5%
