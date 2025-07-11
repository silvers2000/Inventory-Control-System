from flask import Blueprint, request, jsonify
from src.models.inventory import db, Order, OrderItem, Product, InventoryTransaction
from datetime import datetime, date
from decimal import Decimal

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/orders', methods=['GET'])
def get_orders():
    """Get all orders with optional filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        customer_email = request.args.get('customer_email')
        
        query = Order.query
        
        # Apply filters
        if status:
            query = query.filter(Order.status == status)
        
        if customer_email:
            query = query.filter(Order.customer_email.contains(customer_email))
        
        # Order by most recent first
        query = query.order_by(Order.order_date.desc())
        
        # Paginate results
        orders = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'orders': [order.to_dict() for order in orders.items],
            'total': orders.total,
            'pages': orders.pages,
            'current_page': page,
            'per_page': per_page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """Get a specific order by ID"""
    try:
        order = Order.query.get_or_404(order_id)
        return jsonify(order.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/orders', methods=['POST'])
def create_order():
    """Create a new order"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'items' not in data or not data['items']:
            return jsonify({'error': 'Order must contain at least one item'}), 400
        
        # Create order
        order = Order(
            customer_name=data.get('customer_name'),
            customer_email=data.get('customer_email'),
            delivery_date=datetime.strptime(data['delivery_date'], '%Y-%m-%d').date() if data.get('delivery_date') else None,
            status=data.get('status', 'Pending'),
            notes=data.get('notes')
        )
        
        db.session.add(order)
        db.session.flush()  # Get the order ID
        
        total_amount = Decimal('0')
        
        # Process order items
        for item_data in data['items']:
            if 'product_id' not in item_data or 'quantity' not in item_data:
                return jsonify({'error': 'Each item must have product_id and quantity'}), 400
            
            product = Product.query.get(item_data['product_id'])
            if not product:
                return jsonify({'error': f'Product {item_data["product_id"]} not found'}), 404
            
            quantity = int(item_data['quantity'])
            if quantity <= 0:
                return jsonify({'error': 'Quantity must be positive'}), 400
            
            # Check stock availability
            if product.stock_level < quantity:
                return jsonify({
                    'error': f'Insufficient stock for {product.product_name}. Available: {product.stock_level}, Requested: {quantity}'
                }), 400
            
            unit_price = Decimal(str(item_data.get('unit_price', product.unit_price)))
            total_price = unit_price * quantity
            
            order_item = OrderItem(
                order_id=order.order_id,
                product_id=product.product_id,
                quantity=quantity,
                unit_price=unit_price,
                total_price=total_price
            )
            
            db.session.add(order_item)
            total_amount += total_price
            
            # Update product stock
            product.stock_level -= quantity
            product.updated_at = datetime.utcnow()
            
            # Create inventory transaction
            transaction = InventoryTransaction(
                product_id=product.product_id,
                transaction_type='OUT',
                quantity=quantity,
                reference_type='ORDER',
                reference_id=order.order_id,
                notes=f'Stock reduced due to order #{order.order_id}'
            )
            db.session.add(transaction)
        
        # Update order total
        order.total_amount = total_amount
        
        db.session.commit()
        
        return jsonify(order.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/orders/<int:order_id>', methods=['PUT'])
def update_order(order_id):
    """Update an existing order"""
    try:
        order = Order.query.get_or_404(order_id)
        data = request.get_json()
        
        # Update basic order information
        if 'customer_name' in data:
            order.customer_name = data['customer_name']
        if 'customer_email' in data:
            order.customer_email = data['customer_email']
        if 'delivery_date' in data:
            order.delivery_date = datetime.strptime(data['delivery_date'], '%Y-%m-%d').date() if data['delivery_date'] else None
        if 'status' in data:
            order.status = data['status']
        if 'notes' in data:
            order.notes = data['notes']
        
        db.session.commit()
        
        return jsonify(order.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/orders/<int:order_id>', methods=['DELETE'])
def delete_order(order_id):
    """Delete an order (only if status is Pending)"""
    try:
        order = Order.query.get_or_404(order_id)
        
        if order.status not in ['Pending', 'Cancelled']:
            return jsonify({'error': 'Cannot delete order that is not pending or cancelled'}), 400
        
        # If order is pending, restore stock levels
        if order.status == 'Pending':
            for item in order.order_items:
                product = Product.query.get(item.product_id)
                if product:
                    product.stock_level += item.quantity
                    product.updated_at = datetime.utcnow()
                    
                    # Create inventory transaction
                    transaction = InventoryTransaction(
                        product_id=product.product_id,
                        transaction_type='IN',
                        quantity=item.quantity,
                        reference_type='ORDER_CANCELLATION',
                        reference_id=order_id,
                        notes=f'Stock restored due to order #{order_id} cancellation'
                    )
                    db.session.add(transaction)
        
        db.session.delete(order)
        db.session.commit()
        
        return jsonify({'message': 'Order deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/orders/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    """Update order status"""
    try:
        order = Order.query.get_or_404(order_id)
        data = request.get_json()
        
        if 'status' not in data:
            return jsonify({'error': 'Missing status field'}), 400
        
        old_status = order.status
        new_status = data['status']
        
        # If cancelling a pending order, restore stock
        if old_status == 'Pending' and new_status == 'Cancelled':
            for item in order.order_items:
                product = Product.query.get(item.product_id)
                if product:
                    product.stock_level += item.quantity
                    product.updated_at = datetime.utcnow()
                    
                    # Create inventory transaction
                    transaction = InventoryTransaction(
                        product_id=product.product_id,
                        transaction_type='IN',
                        quantity=item.quantity,
                        reference_type='ORDER_CANCELLATION',
                        reference_id=order_id,
                        notes=f'Stock restored due to order #{order_id} cancellation'
                    )
                    db.session.add(transaction)
        
        order.status = new_status
        db.session.commit()
        
        return jsonify(order.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@orders_bp.route('/orders/stats', methods=['GET'])
def get_order_stats():
    """Get order statistics"""
    try:
        total_orders = Order.query.count()
        pending_orders = Order.query.filter_by(status='Pending').count()
        shipped_orders = Order.query.filter_by(status='Shipped').count()
        delivered_orders = Order.query.filter_by(status='Delivered').count()
        cancelled_orders = Order.query.filter_by(status='Cancelled').count()
        
        # Calculate total revenue from delivered orders
        delivered_order_items = db.session.query(Order.total_amount).filter_by(status='Delivered').all()
        total_revenue = sum(order.total_amount for order in delivered_order_items if order.total_amount)
        
        return jsonify({
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'shipped_orders': shipped_orders,
            'delivered_orders': delivered_orders,
            'cancelled_orders': cancelled_orders,
            'total_revenue': float(total_revenue) if total_revenue else 0
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

