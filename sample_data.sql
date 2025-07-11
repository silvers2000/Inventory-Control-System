-- Sample Data for Inventory Control System

-- Insert Categories
INSERT INTO categories (category_name, description) VALUES
('Electronics', 'Electronic devices and components'),
('Office Supplies', 'Office equipment and stationery'),
('Furniture', 'Office and home furniture'),
('Clothing', 'Apparel and accessories'),
('Books', 'Books and educational materials');

-- Insert Suppliers
INSERT INTO suppliers (supplier_name, contact_person, email, phone, address, city, country) VALUES
('TechCorp Solutions', 'John Smith', 'john@techcorp.com', '+1-555-0101', '123 Tech Street', 'San Francisco', 'USA'),
('Office Plus Ltd', 'Sarah Johnson', 'sarah@officeplus.com', '+1-555-0102', '456 Business Ave', 'New York', 'USA'),
('Furniture World', 'Mike Brown', 'mike@furnitureworld.com', '+1-555-0103', '789 Design Blvd', 'Chicago', 'USA'),
('Fashion Hub', 'Lisa Davis', 'lisa@fashionhub.com', '+1-555-0104', '321 Style Street', 'Los Angeles', 'USA'),
('BookMart Inc', 'David Wilson', 'david@bookmart.com', '+1-555-0105', '654 Knowledge Lane', 'Boston', 'USA');

-- Insert Products
INSERT INTO products (product_name, description, category_id, unit_price, stock_level, reorder_level, supplier_id, sku) VALUES
-- Electronics
('Wireless Mouse', 'Ergonomic wireless optical mouse', 1, 29.99, 50, 10, 1, 'TECH-001'),
('USB Keyboard', 'Mechanical USB keyboard with backlight', 1, 79.99, 25, 5, 1, 'TECH-002'),
('Monitor 24"', '24-inch LED monitor with HDMI', 1, 199.99, 15, 3, 1, 'TECH-003'),
('Webcam HD', 'High-definition USB webcam', 1, 49.99, 30, 8, 1, 'TECH-004'),
('USB Cable', 'USB-C to USB-A cable 6ft', 1, 12.99, 100, 20, 1, 'TECH-005'),

-- Office Supplies
('Printer Paper', 'A4 white printer paper 500 sheets', 2, 8.99, 200, 50, 2, 'OFF-001'),
('Ballpoint Pens', 'Blue ballpoint pens pack of 10', 2, 5.99, 150, 30, 2, 'OFF-002'),
('Stapler', 'Heavy-duty office stapler', 2, 15.99, 40, 10, 2, 'OFF-003'),
('File Folders', 'Manila file folders pack of 25', 2, 12.99, 75, 15, 2, 'OFF-004'),
('Sticky Notes', 'Yellow sticky notes 3x3 inch', 2, 3.99, 120, 25, 2, 'OFF-005'),

-- Furniture
('Office Chair', 'Ergonomic office chair with lumbar support', 3, 299.99, 8, 2, 3, 'FUR-001'),
('Desk Lamp', 'LED desk lamp with adjustable arm', 3, 45.99, 20, 5, 3, 'FUR-002'),
('Filing Cabinet', '4-drawer metal filing cabinet', 3, 189.99, 5, 1, 3, 'FUR-003'),
('Bookshelf', '5-tier wooden bookshelf', 3, 129.99, 12, 3, 3, 'FUR-004'),
('Standing Desk', 'Height-adjustable standing desk', 3, 449.99, 3, 1, 3, 'FUR-005'),

-- Clothing
('T-Shirt', 'Cotton crew neck t-shirt', 4, 19.99, 60, 15, 4, 'CLO-001'),
('Jeans', 'Classic blue denim jeans', 4, 59.99, 35, 10, 4, 'CLO-002'),
('Hoodie', 'Pullover hoodie with front pocket', 4, 39.99, 25, 8, 4, 'CLO-003'),
('Sneakers', 'Casual canvas sneakers', 4, 79.99, 18, 5, 4, 'CLO-004'),
('Baseball Cap', 'Adjustable baseball cap', 4, 24.99, 45, 12, 4, 'CLO-005'),

-- Books
('Programming Guide', 'Complete guide to modern programming', 5, 49.99, 30, 8, 5, 'BOO-001'),
('Business Strategy', 'Strategic planning for small businesses', 5, 34.99, 22, 6, 5, 'BOO-002'),
('Design Principles', 'Fundamentals of graphic design', 5, 39.99, 18, 5, 5, 'BOO-003'),
('Data Science', 'Introduction to data science and analytics', 5, 54.99, 15, 4, 5, 'BOO-004'),
('Project Management', 'Agile project management handbook', 5, 42.99, 28, 7, 5, 'BOO-005');

-- Insert Sample Orders
INSERT INTO orders (customer_name, customer_email, order_date, delivery_date, status) VALUES
('Alice Cooper', 'alice@email.com', '2024-01-15 10:30:00', '2024-01-20', 'Delivered'),
('Bob Johnson', 'bob@email.com', '2024-01-16 14:15:00', '2024-01-22', 'Shipped'),
('Carol Smith', 'carol@email.com', '2024-01-17 09:45:00', '2024-01-25', 'Processing'),
('David Brown', 'david@email.com', '2024-01-18 16:20:00', '2024-01-26', 'Pending');

-- Insert Order Items
INSERT INTO order_items (order_id, product_id, quantity, unit_price, total_price) VALUES
-- Order 1
(1, 1, 2, 29.99, 59.98),  -- 2 Wireless Mouse
(1, 6, 5, 8.99, 44.95),   -- 5 Printer Paper
(1, 7, 1, 5.99, 5.99),    -- 1 Ballpoint Pens

-- Order 2
(2, 3, 1, 199.99, 199.99), -- 1 Monitor 24"
(2, 11, 1, 299.99, 299.99), -- 1 Office Chair

-- Order 3
(3, 16, 3, 19.99, 59.97),  -- 3 T-Shirt
(3, 17, 1, 59.99, 59.99),  -- 1 Jeans
(3, 20, 1, 24.99, 24.99),  -- 1 Baseball Cap

-- Order 4
(4, 21, 2, 49.99, 99.98),  -- 2 Programming Guide
(4, 23, 1, 39.99, 39.99);  -- 1 Design Principles

-- Insert Sample Purchase Orders
INSERT INTO purchase_orders (supplier_id, order_date, expected_delivery_date, status) VALUES
(1, '2024-01-10 09:00:00', '2024-01-20', 'Delivered'),
(2, '2024-01-12 11:30:00', '2024-01-22', 'In Transit'),
(3, '2024-01-14 14:00:00', '2024-01-25', 'Pending');

-- Insert Purchase Order Items
INSERT INTO purchase_order_items (purchase_order_id, product_id, quantity, unit_cost, total_cost) VALUES
-- Purchase Order 1 (TechCorp)
(1, 1, 50, 20.00, 1000.00), -- 50 Wireless Mouse
(1, 2, 30, 55.00, 1650.00), -- 30 USB Keyboard
(1, 4, 25, 35.00, 875.00),  -- 25 Webcam HD

-- Purchase Order 2 (Office Plus)
(2, 6, 100, 6.50, 650.00),  -- 100 Printer Paper
(2, 7, 50, 4.00, 200.00),   -- 50 Ballpoint Pens
(2, 10, 30, 2.50, 75.00),   -- 30 Sticky Notes

-- Purchase Order 3 (Furniture World)
(3, 11, 10, 200.00, 2000.00), -- 10 Office Chair
(3, 12, 15, 30.00, 450.00),   -- 15 Desk Lamp
(3, 14, 8, 85.00, 680.00);    -- 8 Bookshelf

