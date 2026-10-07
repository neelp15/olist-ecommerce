-- 03_customer_analysis.sql
USE olist;

-- 1. Lowest-rated categories (200+ reviews)
SELECT COALESCE(t.product_category_name_english, p.product_category_name, 'unknown') AS category,
       COUNT(*) AS reviews,
       ROUND(AVG(r.review_score), 2) AS avg_review
FROM order_items oi
JOIN orders o   ON oi.order_id = o.order_id AND o.order_status = 'delivered'
JOIN products p ON oi.product_id = p.product_id
LEFT JOIN category_translation t ON p.product_category_name = t.product_category_name
JOIN order_reviews r ON oi.order_id = r.order_id
GROUP BY category
HAVING COUNT(*) >= 200
ORDER BY avg_review ASC
LIMIT 10;

-- 2. Repeat customer rate
SELECT ROUND(100 * SUM(order_count > 1) / COUNT(*), 2) AS repeat_pct
FROM (
  SELECT c.customer_unique_id, COUNT(DISTINCT o.order_id) AS order_count
  FROM orders o JOIN customers c ON o.customer_id = c.customer_id
  WHERE o.order_status = 'delivered'
  GROUP BY c.customer_unique_id
) t;

-- 3. Top 10 customers by lifetime spend
SELECT c.customer_unique_id, COUNT(DISTINCT o.order_id) AS orders, ROUND(SUM(oi.price), 2) AS total_spent
FROM customers c
JOIN orders o       ON c.customer_id = o.customer_id
JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.order_status = 'delivered'
GROUP BY c.customer_unique_id
ORDER BY total_spent DESC
LIMIT 10;

-- 4. Does a bad first delivery reduce repeat purchases?
WITH first_orders AS (
  SELECT c.customer_unique_id, o.order_id, o.order_delivered_customer_date, o.order_estimated_delivery_date,
         ROW_NUMBER() OVER (PARTITION BY c.customer_unique_id ORDER BY o.order_purchase_timestamp) AS rn
  FROM orders o JOIN customers c ON o.customer_id = c.customer_id
  WHERE o.order_status = 'delivered' AND o.order_delivered_customer_date IS NOT NULL
),
cust_orders AS (
  SELECT c.customer_unique_id, COUNT(DISTINCT o.order_id) AS n_orders
  FROM orders o JOIN customers c ON o.customer_id = c.customer_id
  WHERE o.order_status = 'delivered'
  GROUP BY c.customer_unique_id
)
SELECT CASE WHEN f.order_delivered_customer_date > f.order_estimated_delivery_date THEN 'First order late' ELSE 'First order on time' END AS first_order,
       COUNT(*) AS customers,
       ROUND(100 * SUM(co.n_orders > 1) / COUNT(*), 2) AS repeat_pct
FROM first_orders f
JOIN cust_orders co ON f.customer_unique_id = co.customer_unique_id
WHERE f.rn = 1
GROUP BY first_order;
