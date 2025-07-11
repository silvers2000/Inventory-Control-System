from flask import Blueprint, request, jsonify
from src.models.inventory import db, Product, Category, Supplier, InventoryTransaction
from datetime import datetime
from decimal import Decimal

products_bp = Blueprint('products', __name__)

@products_bp.route('/products', methods=['GET'])
def get_products():
    """Get all products with optional filtering"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 50, type=int)
        category_id = request.args.get('category_id', type=int)
        low_stock = request.args.get('low_stock', type=bool)
        search = request.args.get('search', '')
        
        query = Product.query
        
        # Apply filters
        if category_id:
            query = query.filter(Product.category_id == category_id)
        
        if low_stock:
            query = query.filter(Product.stock_level <= Product.reorder_level)
        
        if search:
            query = query.filter(
                Product.product_name.contains(search) |
                Product.sku.contains(search) |
                Product.description.contains(search)
            )
        
        # Paginate results
        products = query.paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'products': [product.to_dict() for product in products.items],
            'total': products.total,
            'pages': products.pages,
            'current_page': page,
            'per_page': per_page
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@products_bp.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get a specific product by ID"""
    try:
        product = Product.query.get_or_404(product_id)
        return jsonify(product.to_dict())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@products_bp.route('/products', methods=['POST'])
def create_product():
    """Create a new product"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['product_name', 'unit_price']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # Check if SKU already exists
        if 'sku' in data and data['sku']:
            existing_product = Product.query.filter_by(sku=data['sku']).first()
            if existing_product:
                return jsonify({'error': 'SKU already exists'}), 400
        
        product = Product(
            product_name=data['product_name'],
            description=data.get('description'),
            category_id=data.get('category_id'),
            unit_price=Decimal(str(data['unit_price'])),
            stock_level=data.get('stock_level', 0),
            reorder_level=data.get('reorder_level', 10),
            supplier_id=data.get('supplier_id'),
            sku=data.get('sku')
        )
        
        db.session.add(product)
        db.session.commit()
        
        return jsonify(product.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@products_bp.route('/products/<int:product_id>', methods=['PUT'])
def update_product(product_id):
    """Update an existing product"""
    try:
        product = Product.query.get_or_404(product_id)
        data = request.get_json()
        
        # Check if SKU already exists (excluding current product)
        if 'sku' in data and data['sku']:
            existing_product = Product.query.filter(
                Product.sku == data['sku'],
                Product.product_id != product_id
            ).first()
            if existing_product:
                return jsonify({'error': 'SKU already exists'}), 400
        
        # Update fields
        if 'product_name' in data:
            product.product_name = data['product_name']
        if 'description' in data:
            product.description = data['description']
        if 'category_id' in data:
            product.category_id = data['category_id']
        if 'unit_price' in data:
            product.unit_price = Decimal(str(data['unit_price']))
        if 'reorder_level' in data:
            product.reorder_level = data['reorder_level']
        if 'supplier_id' in data:
            product.supplier_id = data['supplier_id']
        if 'sku' in data:
            product.sku = data['sku']
        
        product.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(product.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@products_bp.route('/products/<int:product_id>', methods=['DELETE'])
def delete_product(product_id):
    """Delete a product"""
    try:
        product = Product.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()
        return jsonify({'message': 'Product deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@products_bp.route('/products/<int:product_id>/adjust-stock', methods=['POST'])
def adjust_stock(product_id):
    """Manually adjust product stock level"""
    try:
        product = Product.query.get_or_404(product_id)
        data = request.get_json()
        
        if 'adjustment' not in data:
            return jsonify({'error': 'Missing adjustment value'}), 400
        
        adjustment = int(data['adjustment'])
        notes = data.get('notes', 'Manual stock adjustment')
        
        # Check if adjustment would result in negative stock
        new_stock = product.stock_level + adjustment
        if new_stock < 0:
            return jsonify({'error': 'Adjustment would result in negative stock'}), 400
        
        # Update stock level
        product.stock_level = new_stock
        product.updated_at = datetime.utcnow()
        
        # Create inventory transaction
        transaction = InventoryTransaction(
            product_id=product_id,
            transaction_type='ADJUSTMENT',
            quantity=abs(adjustment),
            reference_type='ADJUSTMENT',
            notes=notes
        )
        
        db.session.add(transaction)
        db.session.commit()
        
        return jsonify({
            'message': 'Stock adjusted successfully',
            'product': product.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@products_bp.route('/products/low-stock', methods=['GET'])
def get_low_stock_products():
    """Get products with low stock levels"""
    try:
        products = Product.query.filter(
            Product.stock_level <= Product.reorder_level
        ).all()
        
        return jsonify([product.to_dict() for product in products])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@products_bp.route('/categories', methods=['GET'])
def get_categories():
    """Get all categories"""
    try:
        categories = Category.query.all()
        return jsonify([category.to_dict() for category in categories])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@products_bp.route('/categories', methods=['POST'])
def create_category():
    """Create a new category"""
    try:
        data = request.get_json()
        
        if 'category_name' not in data:
            return jsonify({'error': 'Missing category_name'}), 400
        
        category = Category(
            category_name=data['category_name'],
            description=data.get('description')
        )
        
        db.session.add(category)
        db.session.commit()
        
        return jsonify(category.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

