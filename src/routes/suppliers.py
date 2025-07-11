from flask import Blueprint, request, jsonify
from src.models.inventory import db, Supplier, PurchaseOrder, PurchaseOrderItem, Product, InventoryTransaction
from datetime import datetime, date
from decimal import Decimal

suppliers_bp = Blueprint('suppliers', __name__)

@suppliers_bp.route('/suppliers', methods=['GET'])
def get_suppliers():
    """Get all suppliers"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        search = request.args.get('search', '')
        
        query = Supplier.query
        
        if search:
            query = query.filter(
                Supplier.supplier_name.contains(search) |
                Supplier.contact_person.contains(search) |
                Supplier.email.contains(search)
            )
        
        suppliers = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'suppliers': [supplier.to_dict() for supplier in suppliers.items],
            'total': suppliers.total,
            'pages': suppliers.pages,
            'current_page': page,
            'per_page': per_page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@suppliers_bp.route('/suppliers/<int:supplier_id>', methods=['GET'])
def get_supplier(supplier_id):
    """Get a specific supplier by ID"""
    try:
        supplier = Supplier.query.get_or_404(supplier_id)
        return jsonify(supplier.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@suppliers_bp.route('/suppliers', methods=['POST'])
def create_supplier():
    """Create a new supplier"""
    try:
        data = request.get_json()
        
        if 'supplier_name' not in data:
            return jsonify({'error': 'Missing supplier_name'}), 400
        
        supplier = Supplier(
            supplier_name=data['supplier_name'],
            contact_person=data.get('contact_person'),
            email=data.get('email'),
            phone=data.get('phone'),
            address=data.get('address'),
            city=data.get('city'),
            country=data.get('country')
        )
        
        db.session.add(supplier)
        db.session.commit()
        
        return jsonify(supplier.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@suppliers_bp.route('/suppliers/<int:supplier_id>', methods=['PUT'])
def update_supplier(supplier_id):
    """Update an existing supplier"""
    try:
        supplier = Supplier.query.get_or_404(supplier_id)
        data = request.get_json()
        
        # Update fields
        if 'supplier_name' in data:
            supplier.supplier_name = data['supplier_name']
        if 'contact_person' in data:
            supplier.contact_person = data['contact_person']
        if 'email' in data:
            supplier.email = data['email']
        if 'phone' in data:
            supplier.phone = data['phone']
        if 'address' in data:
            supplier.address = data['address']
        if 'city' in data:
            supplier.city = data['city']
        if 'country' in data:
            supplier.country = data['country']
        
        db.session.commit()
        
        return jsonify(supplier.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@suppliers_bp.route('/suppliers/<int:supplier_id>', methods=['DELETE'])
def delete_supplier(supplier_id):
    """Delete a supplier"""
    try:
        supplier = Supplier.query.get_or_404(supplier_id)
        
        # Check if supplier has associated products
        if supplier.products:
            return jsonify({'error': 'Cannot delete supplier with associated products'}), 400
        
        db.session.delete(supplier)
        db.session.commit()
        
        return jsonify({'message': 'Supplier deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

# Purchase Orders endpoints

@suppliers_bp.route('/purchase-orders', methods=['GET'])
def get_purchase_orders():
    """Get all purchase orders"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        supplier_id = request.args.get('supplier_id', type=int)
        
        query = PurchaseOrder.query
        
        if status:
            query = query.filter(PurchaseOrder.status == status)
        
        if supplier_id:
            query = query.filter(PurchaseOrder.supplier_id == supplier_id)
        
        # Order by most recent first
        query = query.order_by(PurchaseOrder.order_date.desc())
        
        purchase_orders = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'purchase_orders': [po.to_dict() for po in purchase_orders.items],
            'total': purchase_orders.total,
            'pages': purchase_orders.pages,
            'current_page': page,
            'per_page': per_page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@suppliers_bp.route('/purchase-orders/<int:purchase_order_id>', methods=['GET'])
def get_purchase_order(purchase_order_id):
    """Get a specific purchase order by ID"""
    try:
        purchase_order = PurchaseOrder.query.get_or_404(purchase_order_id)
        return jsonify(purchase_order.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@suppliers_bp.route('/purchase-orders', methods=['POST'])
def create_purchase_order():
    """Create a new purchase order"""
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'supplier_id' not in data:
            return jsonify({'error': 'Missing supplier_id'}), 400
        
        if 'items' not in data or not data['items']:
            return jsonify({'error': 'Purchase order must contain at least one item'}), 400
        
        # Verify supplier exists
        supplier = Supplier.query.get(data['supplier_id'])
        if not supplier:
            return jsonify({'error': 'Supplier not found'}), 404
        
        # Create purchase order
        purchase_order = PurchaseOrder(
            supplier_id=data['supplier_id'],
            expected_delivery_date=datetime.strptime(data['expected_delivery_date'], '%Y-%m-%d').date() if data.get('expected_delivery_date') else None,
            status=data.get('status', 'Pending'),
            notes=data.get('notes')
        )
        
        db.session.add(purchase_order)
        db.session.flush()  # Get the purchase order ID
        
        total_amount = Decimal('0')
        
        # Process purchase order items
        for item_data in data['items']:
            if 'product_id' not in item_data or 'quantity' not in item_data or 'unit_cost' not in item_data:
                return jsonify({'error': 'Each item must have product_id, quantity, and unit_cost'}), 400
            
            product = Product.query.get(item_data['product_id'])
            if not product:
                return jsonify({'error': f'Product {item_data["product_id"]} not found'}), 404
            
            quantity = int(item_data['quantity'])
            unit_cost = Decimal(str(item_data['unit_cost']))
            total_cost = unit_cost * quantity
            
            purchase_order_item = PurchaseOrderItem(
                purchase_order_id=purchase_order.purchase_order_id,
                product_id=product.product_id,
                quantity=quantity,
                unit_cost=unit_cost,
                total_cost=total_cost
            )
            
            db.session.add(purchase_order_item)
            total_amount += total_cost
        
        # Update purchase order total
        purchase_order.total_amount = total_amount
        
        db.session.commit()
        
        return jsonify(purchase_order.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@suppliers_bp.route('/purchase-orders/<int:purchase_order_id>', methods=['PUT'])
def update_purchase_order(purchase_order_id):
    """Update an existing purchase order"""
    try:
        purchase_order = PurchaseOrder.query.get_or_404(purchase_order_id)
        data = request.get_json()
        
        # Update basic purchase order information
        if 'expected_delivery_date' in data:
            purchase_order.expected_delivery_date = datetime.strptime(data['expected_delivery_date'], '%Y-%m-%d').date() if data['expected_delivery_date'] else None
        if 'status' in data:
            purchase_order.status = data['status']
        if 'notes' in data:
            purchase_order.notes = data['notes']
        
        db.session.commit()
        
        return jsonify(purchase_order.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@suppliers_bp.route('/purchase-orders/<int:purchase_order_id>/receive', methods=['POST'])
def receive_purchase_order(purchase_order_id):
    """Mark purchase order as received and update stock levels"""
    try:
        purchase_order = PurchaseOrder.query.get_or_404(purchase_order_id)
        
        if purchase_order.status == 'Delivered':
            return jsonify({'error': 'Purchase order already received'}), 400
        
        # Update stock levels for all items
        for item in purchase_order.purchase_order_items:
            product = Product.query.get(item.product_id)
            if product:
                product.stock_level += item.quantity
                product.updated_at = datetime.utcnow()
                
                # Create inventory transaction
                transaction = InventoryTransaction(
                    product_id=product.product_id,
                    transaction_type='IN',
                    quantity=item.quantity,
                    reference_type='PURCHASE_ORDER',
                    reference_id=purchase_order_id,
                    notes=f'Stock increased due to purchase order #{purchase_order_id}'
                )
                db.session.add(transaction)
        
        # Update purchase order status
        purchase_order.status = 'Delivered'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Purchase order received successfully',
            'purchase_order': purchase_order.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@suppliers_bp.route('/purchase-orders/<int:purchase_order_id>', methods=['DELETE'])
def delete_purchase_order(purchase_order_id):
    """Delete a purchase order (only if status is Pending)"""
    try:
        purchase_order = PurchaseOrder.query.get_or_404(purchase_order_id)
        
        if purchase_order.status not in ['Pending', 'Cancelled']:
            return jsonify({'error': 'Cannot delete purchase order that is not pending or cancelled'}), 400
        
        db.session.delete(purchase_order)
        db.session.commit()
        
        return jsonify({'message': 'Purchase order deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

