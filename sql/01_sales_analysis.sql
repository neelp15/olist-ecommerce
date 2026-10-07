-- 01_sales_analysis.sql
USE olist;

-- 1. Monthly revenue and orders (delivered)
SELECT DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m') AS month,
       COUNT(DISTINCT o.order_id) AS orders,
       ROUND(SUM(oi.price), 2)    AS revenue
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY month
ORDER BY month;

-- 2. Top 10 categories by revenue (English names; LEFT JOIN keeps untranslated categories)
SELECT COALESCE(t.product_category_name_english, p.product_category_name, 'unknown') AS category,
       ROUND(SUM(oi.price), 2) AS revenue,
       COUNT(*)                AS items_sold
FROM order_items oi
JOIN orders o   ON oi.order_id = o.order_id AND o.order_status = 'delivered'
JOIN products p ON oi.product_id = p.product_id
LEFT JOIN category_translation t ON p.product_category_name = t.product_category_name
GROUP BY category
ORDER BY revenue DESC
LIMIT 10;

-- 3. Average order value
SELECT ROUND(SUM(oi.price) / COUNT(DISTINCT oi.order_id), 2) AS avg_order_value
FROM order_items oi
JOIN orders o ON oi.order_id = o.order_id
WHERE o.order_status = 'delivered';

-- 4. Payment method share
SELECT payment_type,
       COUNT(*) AS payments,
       ROUND(100 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS pct
FROM order_payments
WHERE payment_type <> 'not_defined'
GROUP BY payment_type
ORDER BY payments DESC;

-- 5. Rank categories by revenue within each year (window function)
SELECT yr, category, revenue, rnk
FROM (
  SELECT yr, category, revenue,
         RANK() OVER (PARTITION BY yr ORDER BY revenue DESC) AS rnk
  FROM (
    SELECT YEAR(o.order_purchase_timestamp) AS yr,
           COALESCE(t.product_category_name_english, p.product_category_name, 'unknown') AS category,
           ROUND(SUM(oi.price), 2) AS revenue
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p     ON oi.product_id = p.product_id
    LEFT JOIN category_translation t ON p.product_category_name = t.product_category_name
    WHERE o.order_status = 'delivered'
    GROUP BY yr, category
  ) x
) y
WHERE rnk <= 5
ORDER BY yr, rnk;

-- 6. Month-over-month revenue growth (LAG)
SELECT month, revenue,
       ROUND(100 * (revenue - LAG(revenue) OVER (ORDER BY month)) / LAG(revenue) OVER (ORDER BY month), 1) AS mom_growth_pct
FROM (
  SELECT DATE_FORMAT(o.order_purchase_timestamp, '%Y-%m') AS month, ROUND(SUM(oi.price), 2) AS revenue
  FROM orders o JOIN order_items oi ON o.order_id = oi.order_id
  WHERE o.order_status = 'delivered'
  GROUP BY month
) m
ORDER BY month;
