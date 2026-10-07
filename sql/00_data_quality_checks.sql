-- 00_data_quality_checks.sql
USE olist;

-- Row counts
SELECT 'orders' AS tbl, COUNT(*) AS n FROM orders
UNION ALL SELECT 'order_items', COUNT(*) FROM order_items
UNION ALL SELECT 'order_reviews', COUNT(*) FROM order_reviews
UNION ALL SELECT 'customers', COUNT(*) FROM customers
UNION ALL SELECT 'products', COUNT(*) FROM products;

-- Order status breakdown (we analyse only 'delivered')
SELECT order_status, COUNT(*) AS orders FROM orders GROUP BY order_status ORDER BY orders DESC;

-- Delivered orders with no delivery date (excluded from delivery analysis)
SELECT COUNT(*) AS delivered_without_date
FROM orders
WHERE order_status = 'delivered' AND order_delivered_customer_date IS NULL;

-- Orders with more than one review
SELECT COUNT(*) AS orders_with_multiple_reviews
FROM (SELECT order_id FROM order_reviews GROUP BY order_id HAVING COUNT(*) > 1) t;

-- Products with no category
SELECT COUNT(*) AS products_without_category FROM products WHERE product_category_name IS NULL;
