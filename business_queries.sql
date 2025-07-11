-- Business Logic SQL Queries for Inventory Control System

-- 1. Update stock levels after sales (handled by triggers, but manual query for reference)
-- This query would be used if not using triggers
/*
UPDATE products 
SET stock_level = stock_level - :quantity,
    updated_at = CURRENT_TIMESTAMP
WHERE product_id = :product_id 
AND stock_level >= :quantity;
*/

-- 2. Identify low-inventory items requiring reordering
-- Products where current stock is at or below reorder level
CREATE VIEW IF NOT EXISTS low_inventory_items AS
SELECT 
    p.product_id,
    p.product_name,
    p.sku,
    c.category_name,
    p.stock_level,
    p.reorder_level,
    p.unit_price,
    s.supplier_name,
    s.email as supplier_email,
    s.phone as supplier_phone,
    (p.reorder_level - p.stock_level) as shortage_quantity
FROM products p
LEFT JOIN categories c ON p.category_id = c.category_id
LEFT JOIN suppliers s ON p.supplier_id = s.supplier_id
WHERE p.stock_level <= p.reorder_level
ORDER BY (p.reorder_level - p.stock_level) DESC;

-- 3. Generate reports on product sales by category
CREATE VIEW IF NOT EXISTS sales_by_category AS
SELECT 
    c.category_name,
    COUNT(DISTINCT oi.product_id) as products_sold,
    SUM(oi.quantity) as total_quantity_sold,
    SUM(oi.total_price) as total_revenue,
    AVG(oi.unit_price) as avg_selling_price,
    COUNT(DISTINCT oi.order_id) as number_of_orders
FROM categories c
LEFT JOIN products p ON c.category_id = p.category_id
LEFT JOIN order_items oi ON p.product_id = oi.product_id
LEFT JOIN orders o ON oi.order_id = o.order_id
WHERE o.status IN ('Delivered', 'Shipped')
GROUP BY c.category_id, c.category_name
ORDER BY total_revenue DESC;

-- 4. Product performance report
CREATE VIEW IF NOT EXISTS product_performance AS
SELECT 
    p.product_id,
    p.product_name,
    p.sku,
    c.category_name,
    p.unit_price,
    p.stock_level,
    COALESCE(SUM(oi.quantity), 0) as total_sold,
    COALESCE(SUM(oi.total_price), 0) as total_revenue,
    COALESCE(COUNT(DISTINCT oi.order_id), 0) as times_ordered,
    p.stock_level + COALESCE(SUM(oi.quantity), 0) as initial_stock
FROM products p
LEFT JOIN categories c ON p.category_id = c.category_id
LEFT JOIN order_items oi ON p.product_id = oi.product_id
LEFT JOIN orders o ON oi.order_id = o.order_id AND o.status IN ('Delivered', 'Shipped')
GROUP BY p.product_id, p.product_name, p.sku, c.category_name, p.unit_price, p.stock_level
ORDER BY total_revenue DESC;

-- 5. Monthly sales report
CREATE VIEW IF NOT EXISTS monthly_sales AS
SELECT 
    strftime('%Y-%m', o.order_date) as month_year,
    COUNT(DISTINCT o.order_id) as total_orders,
    SUM(o.total_amount) as total_revenue,
    AVG(o.total_amount) as avg_order_value,
    SUM(oi.quantity) as total_items_sold
FROM orders o
LEFT JOIN order_items oi ON o.order_id = oi.order_id
WHERE o.status IN ('Delivered', 'Shipped')
GROUP BY strftime('%Y-%m', o.order_date)
ORDER BY month_year DESC;

-- 6. Supplier performance report
CREATE VIEW IF NOT EXISTS supplier_performance AS
SELECT 
    s.supplier_id,
    s.supplier_name,
    s.contact_person,
    s.email,
    COUNT(DISTINCT p.product_id) as products_supplied,
    COUNT(DISTINCT po.purchase_order_id) as purchase_orders,
    SUM(po.total_amount) as total_purchase_value,
    AVG(po.total_amount) as avg_purchase_order_value
FROM suppliers s
LEFT JOIN products p ON s.supplier_id = p.supplier_id
LEFT JOIN purchase_orders po ON s.supplier_id = po.supplier_id
GROUP BY s.supplier_id, s.supplier_name, s.contact_person, s.email
ORDER BY total_purchase_value DESC;

-- 7. Inventory valuation report
CREATE VIEW IF NOT EXISTS inventory_valuation AS
SELECT 
    c.category_name,
    COUNT(p.product_id) as product_count,
    SUM(p.stock_level) as total_units,
    SUM(p.stock_level * p.unit_price) as total_value,
    AVG(p.unit_price) as avg_unit_price
FROM categories c
LEFT JOIN products p ON c.category_id = p.category_id
WHERE p.stock_level > 0
GROUP BY c.category_id, c.category_name
ORDER BY total_value DESC;

-- 8. Recent transactions report
CREATE VIEW IF NOT EXISTS recent_transactions AS
SELECT 
    it.transaction_id,
    p.product_name,
    p.sku,
    it.transaction_type,
    it.quantity,
    it.reference_type,
    it.reference_id,
    it.transaction_date,
    it.notes
FROM inventory_transactions it
JOIN products p ON it.product_id = p.product_id
ORDER BY it.transaction_date DESC;

-- 9. Top selling products
CREATE VIEW IF NOT EXISTS top_selling_products AS
SELECT 
    p.product_id,
    p.product_name,
    p.sku,
    c.category_name,
    SUM(oi.quantity) as total_sold,
    SUM(oi.total_price) as total_revenue,
    COUNT(DISTINCT oi.order_id) as order_frequency,
    p.stock_level as current_stock
FROM products p
JOIN categories c ON p.category_id = c.category_id
JOIN order_items oi ON p.product_id = oi.product_id
JOIN orders o ON oi.order_id = o.order_id
WHERE o.status IN ('Delivered', 'Shipped')
GROUP BY p.product_id, p.product_name, p.sku, c.category_name, p.stock_level
ORDER BY total_sold DESC
LIMIT 20;

-- 10. Stock movement analysis
CREATE VIEW IF NOT EXISTS stock_movement_analysis AS
SELECT 
    p.product_id,
    p.product_name,
    p.sku,
    p.stock_level as current_stock,
    SUM(CASE WHEN it.transaction_type = 'IN' THEN it.quantity ELSE 0 END) as total_received,
    SUM(CASE WHEN it.transaction_type = 'OUT' THEN it.quantity ELSE 0 END) as total_sold,
    SUM(CASE WHEN it.transaction_type = 'ADJUSTMENT' THEN it.quantity ELSE 0 END) as total_adjustments,
    COUNT(it.transaction_id) as total_transactions
FROM products p
LEFT JOIN inventory_transactions it ON p.product_id = it.product_id
GROUP BY p.product_id, p.product_name, p.sku, p.stock_level
ORDER BY total_transactions DESC;

