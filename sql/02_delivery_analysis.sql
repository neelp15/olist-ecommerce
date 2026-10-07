-- 02_delivery_analysis.sql
USE olist;

-- 1. Late vs on-time: orders and average review (review averaged per order first)
WITH review_per_order AS (
  SELECT order_id, AVG(review_score) AS review_score FROM order_reviews GROUP BY order_id
)
SELECT CASE WHEN o.order_delivered_customer_date > o.order_estimated_delivery_date
            THEN 'Late' ELSE 'On time' END AS delivery_status,
       COUNT(*) AS orders,
       ROUND(AVG(r.review_score), 2) AS avg_review
FROM orders o
JOIN review_per_order r ON o.order_id = r.order_id
WHERE o.order_status = 'delivered'
  AND o.order_delivered_customer_date IS NOT NULL
GROUP BY delivery_status;

-- 2. Late delivery % by customer state
SELECT c.customer_state,
       COUNT(*) AS total_orders,
       ROUND(100 * SUM(o.order_delivered_customer_date > o.order_estimated_delivery_date) / COUNT(*), 1) AS late_pct
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_status = 'delivered' AND o.order_delivered_customer_date IS NOT NULL
GROUP BY c.customer_state
HAVING COUNT(*) > 500
ORDER BY late_pct DESC;

-- 3. Average review by delay bucket
WITH review_per_order AS (
  SELECT order_id, AVG(review_score) AS review_score FROM order_reviews GROUP BY order_id
),
delays AS (
  SELECT o.order_id,
         CEIL(TIMESTAMPDIFF(SECOND, o.order_estimated_delivery_date, o.order_delivered_customer_date) / 86400) AS delay_days
  FROM orders o
  WHERE o.order_status = 'delivered' AND o.order_delivered_customer_date IS NOT NULL
)
SELECT CASE WHEN d.delay_days < 0 THEN '1 Early'
            WHEN d.delay_days = 0 THEN '2 On time'
            WHEN d.delay_days <= 3 THEN '3 1-3 days late'
            WHEN d.delay_days <= 7 THEN '4 4-7 days late'
            ELSE '5 7+ days late' END AS bucket,
       COUNT(*) AS orders,
       ROUND(AVG(r.review_score), 2) AS avg_review
FROM delays d
JOIN review_per_order r ON d.order_id = r.order_id
GROUP BY bucket
ORDER BY bucket;

-- 4. Average delivery time (days) by state
SELECT c.customer_state,
       ROUND(AVG(TIMESTAMPDIFF(HOUR, o.order_purchase_timestamp, o.order_delivered_customer_date)) / 24, 1) AS avg_delivery_days
FROM orders o
JOIN customers c ON o.customer_id = c.customer_id
WHERE o.order_status = 'delivered' AND o.order_delivered_customer_date IS NOT NULL
GROUP BY c.customer_state
ORDER BY avg_delivery_days DESC;
