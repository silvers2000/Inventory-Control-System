from flask import Blueprint, request, jsonify
from src.models.inventory import db, Product, Category, Order, OrderItem, Supplier, InventoryTransaction
from sqlalchemy import func, text
from datetime import datetime, timedelta

reports_bp = Blueprint('reports', __name__)

@reports_bp.route('/reports/low-inventory', methods=['GET'])
def low_inventory_report():
    """Get products with low inventory levels"""
    try:
        query = text("""
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
            ORDER BY (p.reorder_level - p.stock_level) DESC
        """)
        
        result = db.session.execute(query)
        items = []
        
        for row in result:
            items.append({
                'product_id': row.product_id,
                'product_name': row.product_name,
                'sku': row.sku,
                'category_name': row.category_name,
                'stock_level': row.stock_level,
                'reorder_level': row.reorder_level,
                'unit_price': float(row.unit_price) if row.unit_price else 0,
                'supplier_name': row.supplier_name,
                'supplier_email': row.supplier_email,
                'supplier_phone': row.supplier_phone,
                'shortage_quantity': row.shortage_quantity
            })
        
        return jsonify({
            'low_inventory_items': items,
            'total_items': len(items)
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/reports/sales-by-category', methods=['GET'])
def sales_by_category_report():
    """Get sales report grouped by category"""
    try:
        query = text("""
            SELECT 
                c.category_name,
                COUNT(DISTINCT oi.product_id) as products_sold,
                COALESCE(SUM(oi.quantity), 0) as total_quantity_sold,
                COALESCE(SUM(oi.total_price), 0) as total_revenue,
                COALESCE(AVG(oi.unit_price), 0) as avg_selling_price,
                COUNT(DISTINCT oi.order_id) as number_of_orders
            FROM categories c
            LEFT JOIN products p ON c.category_id = p.category_id
            LEFT JOIN order_items oi ON p.product_id = oi.product_id
            LEFT JOIN orders o ON oi.order_id = o.order_id
            WHERE o.status IN ('Delivered', 'Shipped') OR o.status IS NULL
            GROUP BY c.category_id, c.category_name
            ORDER BY total_revenue DESC
        """)
        
        result = db.session.execute(query)
        categories = []
        
        for row in result:
            categories.append({
                'category_name': row.category_name,
                'products_sold': row.products_sold,
                'total_quantity_sold': row.total_quantity_sold,
                'total_revenue': float(row.total_revenue) if row.total_revenue else 0,
                'avg_selling_price': float(row.avg_selling_price) if row.avg_selling_price else 0,
                'number_of_orders': row.number_of_orders
            })
        
        return jsonify({
            'sales_by_category': categories
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/reports/product-performance', methods=['GET'])
def product_performance_report():
    """Get product performance report"""
    try:
        limit = request.args.get('limit', 20, type=int)
        
        query = text(f"""
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
            ORDER BY total_revenue DESC
            LIMIT {limit}
        """)
        
        result = db.session.execute(query)
        products = []
        
        for row in result:
            products.append({
                'product_id': row.product_id,
                'product_name': row.product_name,
                'sku': row.sku,
                'category_name': row.category_name,
                'unit_price': float(row.unit_price) if row.unit_price else 0,
                'stock_level': row.stock_level,
                'total_sold': row.total_sold,
                'total_revenue': float(row.total_revenue) if row.total_revenue else 0,
                'times_ordered': row.times_ordered,
                'initial_stock': row.initial_stock
            })
        
        return jsonify({
            'product_performance': products
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/reports/monthly-sales', methods=['GET'])
def monthly_sales_report():
    """Get monthly sales report"""
    try:
        months = request.args.get('months', 12, type=int)
        
        query = text(f"""
            SELECT 
                strftime('%Y-%m', o.order_date) as month_year,
                COUNT(DISTINCT o.order_id) as total_orders,
                COALESCE(SUM(o.total_amount), 0) as total_revenue,
                COALESCE(AVG(o.total_amount), 0) as avg_order_value,
                COALESCE(SUM(oi.quantity), 0) as total_items_sold
            FROM orders o
            LEFT JOIN order_items oi ON o.order_id = oi.order_id
            WHERE o.status IN ('Delivered', 'Shipped')
            AND o.order_date >= date('now', '-{months} months')
            GROUP BY strftime('%Y-%m', o.order_date)
            ORDER BY month_year DESC
        """)
        
        result = db.session.execute(query)
        monthly_data = []
        
        for row in result:
            monthly_data.append({
                'month_year': row.month_year,
                'total_orders': row.total_orders,
                'total_revenue': float(row.total_revenue) if row.total_revenue else 0,
                'avg_order_value': float(row.avg_order_value) if row.avg_order_value else 0,
                'total_items_sold': row.total_items_sold
            })
        
        return jsonify({
            'monthly_sales': monthly_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/reports/inventory-valuation', methods=['GET'])
def inventory_valuation_report():
    """Get inventory valuation report by category"""
    try:
        query = text("""
            SELECT 
                c.category_name,
                COUNT(p.product_id) as product_count,
                SUM(p.stock_level) as total_units,
                SUM(p.stock_level * p.unit_price) as total_value,
                AVG(p.unit_price) as avg_unit_price
            FROM categories c
            LEFT JOIN products p ON c.category_id = p.category_id
            WHERE p.stock_level > 0 OR p.stock_level IS NULL
            GROUP BY c.category_id, c.category_name
            ORDER BY total_value DESC
        """)
        
        result = db.session.execute(query)
        valuation_data = []
        
        for row in result:
            valuation_data.append({
                'category_name': row.category_name,
                'product_count': row.product_count,
                'total_units': row.total_units or 0,
                'total_value': float(row.total_value) if row.total_value else 0,
                'avg_unit_price': float(row.avg_unit_price) if row.avg_unit_price else 0
            })
        
        return jsonify({
            'inventory_valuation': valuation_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/reports/top-selling-products', methods=['GET'])
def top_selling_products_report():
    """Get top selling products"""
    try:
        limit = request.args.get('limit', 10, type=int)
        
        query = text(f"""
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
            LIMIT {limit}
        """)
        
        result = db.session.execute(query)
        top_products = []
        
        for row in result:
            top_products.append({
                'product_id': row.product_id,
                'product_name': row.product_name,
                'sku': row.sku,
                'category_name': row.category_name,
                'total_sold': row.total_sold,
                'total_revenue': float(row.total_revenue) if row.total_revenue else 0,
                'order_frequency': row.order_frequency,
                'current_stock': row.current_stock
            })
        
        return jsonify({
            'top_selling_products': top_products
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/reports/recent-transactions', methods=['GET'])
def recent_transactions_report():
    """Get recent inventory transactions"""
    try:
        limit = request.args.get('limit', 50, type=int)
        
        transactions = InventoryTransaction.query.join(Product).order_by(
            InventoryTransaction.transaction_date.desc()
        ).limit(limit).all()
        
        transaction_data = []
        for transaction in transactions:
            transaction_data.append({
                'transaction_id': transaction.transaction_id,
                'product_name': transaction.product.product_name,
                'sku': transaction.product.sku,
                'transaction_type': transaction.transaction_type,
                'quantity': transaction.quantity,
                'reference_type': transaction.reference_type,
                'reference_id': transaction.reference_id,
                'transaction_date': transaction.transaction_date.isoformat() if transaction.transaction_date else None,
                'notes': transaction.notes
            })
        
        return jsonify({
            'recent_transactions': transaction_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@reports_bp.route('/reports/dashboard-stats', methods=['GET'])
def dashboard_stats():
    """Get dashboard statistics"""
    try:
        # Total products
        total_products = Product.query.count()
        
        # Low stock products
        low_stock_count = Product.query.filter(
            Product.stock_level <= Product.reorder_level
        ).count()
        
        # Total orders
        total_orders = Order.query.count()
        
        # Pending orders
        pending_orders = Order.query.filter_by(status='Pending').count()
        
        # Total revenue (delivered orders)
        revenue_result = db.session.query(func.sum(Order.total_amount)).filter_by(status='Delivered').scalar()
        total_revenue = float(revenue_result) if revenue_result else 0
        
        # Total inventory value
        inventory_value_result = db.session.query(
            func.sum(Product.stock_level * Product.unit_price)
        ).scalar()
        total_inventory_value = float(inventory_value_result) if inventory_value_result else 0
        
        # Recent orders (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_orders = Order.query.filter(Order.order_date >= week_ago).count()
        
        # Categories count
        total_categories = Category.query.count()
        
        # Suppliers count
        total_suppliers = Supplier.query.count()
        
        return jsonify({
            'total_products': total_products,
            'low_stock_count': low_stock_count,
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'total_revenue': total_revenue,
            'total_inventory_value': total_inventory_value,
            'recent_orders': recent_orders,
            'total_categories': total_categories,
            'total_suppliers': total_suppliers
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

