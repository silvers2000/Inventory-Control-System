// Global variables
let currentSection = 'dashboard';
let currentPage = 1;
let categories = [];
let suppliers = [];
let products = [];

// API Base URL
const API_BASE = '/api';

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

async function initializeApp() {
    try {
        showLoading();
        
        // Load initial data
        await Promise.all([
            loadCategories(),
            loadSuppliers(),
            loadDashboardStats(),
            loadRecentTransactions()
        ]);
        
        // Set up event listeners
        setupEventListeners();
        
        // Show dashboard by default
        showSection('dashboard');
        
        hideLoading();
    } catch (error) {
        console.error('Error initializing app:', error);
        showToast('Error loading application', 'error');
        hideLoading();
    }
}

function setupEventListeners() {
    // Navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const section = link.dataset.section;
            showSection(section);
        });
    });

    // Search and filters
    document.getElementById('product-search')?.addEventListener('input', debounce(searchProducts, 300));
    document.getElementById('category-filter')?.addEventListener('change', filterProducts);
    document.getElementById('low-stock-filter')?.addEventListener('change', filterProducts);
    document.getElementById('order-status-filter')?.addEventListener('change', filterOrders);
    document.getElementById('supplier-search')?.addEventListener('input', debounce(searchSuppliers, 300));

    // Forms
    document.getElementById('add-product-form')?.addEventListener('submit', handleAddProduct);
    document.getElementById('add-order-form')?.addEventListener('submit', handleAddOrder);
    document.getElementById('add-supplier-form')?.addEventListener('submit', handleAddSupplier);

    // Modal close events
    document.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal')) {
            closeModal(e.target.id);
        }
    });
}

// Navigation functions
function showSection(sectionName) {
    // Update navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    document.querySelector(`[data-section="${sectionName}"]`).classList.add('active');

    // Update content
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });
    document.getElementById(sectionName).classList.add('active');

    currentSection = sectionName;

    // Load section-specific data
    switch (sectionName) {
        case 'dashboard':
            loadDashboardStats();
            loadRecentTransactions();
            break;
        case 'products':
            loadProducts();
            break;
        case 'orders':
            loadOrders();
            break;
        case 'suppliers':
            loadSuppliers();
            break;
        case 'reports':
            // Reports are loaded on demand
            break;
    }
}

// API functions
async function apiCall(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'API request failed');
        }

        return await response.json();
    } catch (error) {
        console.error('API Error:', error);
        throw error;
    }
}

// Dashboard functions
async function loadDashboardStats() {
    try {
        const stats = await apiCall('/reports/dashboard-stats');
        
        document.getElementById('total-products').textContent = stats.total_products;
        document.getElementById('low-stock-count').textContent = stats.low_stock_count;
        document.getElementById('total-orders').textContent = stats.total_orders;
        document.getElementById('total-revenue').textContent = `$${stats.total_revenue.toFixed(2)}`;
    } catch (error) {
        showToast('Error loading dashboard stats', 'error');
    }
}

async function loadRecentTransactions() {
    try {
        const data = await apiCall('/reports/recent-transactions?limit=5');
        const container = document.getElementById('recent-transactions');
        
        if (data.recent_transactions.length === 0) {
            container.innerHTML = '<p class="text-gray-500">No recent transactions</p>';
            return;
        }

        container.innerHTML = data.recent_transactions.map(transaction => `
            <div class="activity-item">
                <div class="activity-icon">
                    <i class="fas fa-${getTransactionIcon(transaction.transaction_type)}"></i>
                </div>
                <div class="activity-content">
                    <h4>${transaction.product_name}</h4>
                    <p>${transaction.transaction_type} - ${transaction.quantity} units - ${formatDate(transaction.transaction_date)}</p>
                </div>
            </div>
        `).join('');
    } catch (error) {
        showToast('Error loading recent transactions', 'error');
    }
}

function getTransactionIcon(type) {
    switch (type) {
        case 'IN': return 'arrow-up';
        case 'OUT': return 'arrow-down';
        case 'ADJUSTMENT': return 'edit';
        default: return 'exchange-alt';
    }
}

// Products functions
async function loadProducts(page = 1) {
    try {
        showLoading();
        const searchTerm = document.getElementById('product-search')?.value || '';
        const categoryId = document.getElementById('category-filter')?.value || '';
        const lowStock = document.getElementById('low-stock-filter')?.checked || false;

        let url = `/products?page=${page}&per_page=20`;
        if (searchTerm) url += `&search=${encodeURIComponent(searchTerm)}`;
        if (categoryId) url += `&category_id=${categoryId}`;
        if (lowStock) url += `&low_stock=true`;

        const data = await apiCall(url);
        products = data.products;
        
        renderProductsTable(data.products);
        renderPagination('products-pagination', data.current_page, data.pages, loadProducts);
        
        hideLoading();
    } catch (error) {
        showToast('Error loading products', 'error');
        hideLoading();
    }
}

function renderProductsTable(products) {
    const tbody = document.getElementById('products-table-body');
    
    if (products.length === 0) {
        tbody.innerHTML = '<tr><td colspan="7" class="text-center">No products found</td></tr>';
        return;
    }

    tbody.innerHTML = products.map(product => `
        <tr>
            <td>${product.sku || 'N/A'}</td>
            <td>${product.product_name}</td>
            <td>${product.category_name || 'Uncategorized'}</td>
            <td>$${product.unit_price.toFixed(2)}</td>
            <td>${product.stock_level}</td>
            <td>
                <span class="status-badge ${product.is_low_stock ? 'low-stock' : 'in-stock'}">
                    ${product.is_low_stock ? 'Low Stock' : 'In Stock'}
                </span>
            </td>
            <td>
                <div class="action-buttons">
                    <button class="action-btn edit" onclick="editProduct(${product.product_id})" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="action-btn delete" onclick="deleteProduct(${product.product_id})" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

async function searchProducts() {
    currentPage = 1;
    await loadProducts(currentPage);
}

async function filterProducts() {
    currentPage = 1;
    await loadProducts(currentPage);
}

// Categories functions
async function loadCategories() {
    try {
        const data = await apiCall('/categories');
        categories = data;
        
        // Populate category dropdowns
        const categorySelects = document.querySelectorAll('#category-filter, #product-category');
        categorySelects.forEach(select => {
            const currentValue = select.value;
            select.innerHTML = select.id === 'category-filter' ? 
                '<option value="">All Categories</option>' : 
                '<option value="">Select Category</option>';
            
            data.forEach(category => {
                select.innerHTML += `<option value="${category.category_id}">${category.category_name}</option>`;
            });
            
            select.value = currentValue;
        });
    } catch (error) {
        showToast('Error loading categories', 'error');
    }
}

// Suppliers functions
async function loadSuppliers(page = 1) {
    try {
        if (currentSection === 'suppliers') showLoading();
        
        const searchTerm = document.getElementById('supplier-search')?.value || '';
        let url = `/suppliers?page=${page}&per_page=20`;
        if (searchTerm) url += `&search=${encodeURIComponent(searchTerm)}`;

        const data = await apiCall(url);
        suppliers = data.suppliers;
        
        if (currentSection === 'suppliers') {
            renderSuppliersTable(data.suppliers);
            renderPagination('suppliers-pagination', data.current_page, data.pages, loadSuppliers);
        }
        
        // Populate supplier dropdown
        const supplierSelect = document.getElementById('product-supplier');
        if (supplierSelect) {
            const currentValue = supplierSelect.value;
            supplierSelect.innerHTML = '<option value="">Select Supplier</option>';
            data.suppliers.forEach(supplier => {
                supplierSelect.innerHTML += `<option value="${supplier.supplier_id}">${supplier.supplier_name}</option>`;
            });
            supplierSelect.value = currentValue;
        }
        
        if (currentSection === 'suppliers') hideLoading();
    } catch (error) {
        showToast('Error loading suppliers', 'error');
        if (currentSection === 'suppliers') hideLoading();
    }
}

function renderSuppliersTable(suppliers) {
    const tbody = document.getElementById('suppliers-table-body');
    
    if (suppliers.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center">No suppliers found</td></tr>';
        return;
    }

    tbody.innerHTML = suppliers.map(supplier => `
        <tr>
            <td>${supplier.supplier_name}</td>
            <td>${supplier.contact_person || 'N/A'}</td>
            <td>${supplier.email || 'N/A'}</td>
            <td>${supplier.phone || 'N/A'}</td>
            <td>${supplier.city || 'N/A'}</td>
            <td>
                <div class="action-buttons">
                    <button class="action-btn edit" onclick="editSupplier(${supplier.supplier_id})" title="Edit">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="action-btn delete" onclick="deleteSupplier(${supplier.supplier_id})" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

async function searchSuppliers() {
    currentPage = 1;
    await loadSuppliers(currentPage);
}

// Orders functions
async function loadOrders(page = 1) {
    try {
        showLoading();
        const status = document.getElementById('order-status-filter')?.value || '';

        let url = `/orders?page=${page}&per_page=20`;
        if (status) url += `&status=${status}`;

        const data = await apiCall(url);
        
        renderOrdersTable(data.orders);
        renderPagination('orders-pagination', data.current_page, data.pages, loadOrders);
        
        hideLoading();
    } catch (error) {
        showToast('Error loading orders', 'error');
        hideLoading();
    }
}

function renderOrdersTable(orders) {
    const tbody = document.getElementById('orders-table-body');
    
    if (orders.length === 0) {
        tbody.innerHTML = '<tr><td colspan="6" class="text-center">No orders found</td></tr>';
        return;
    }

    tbody.innerHTML = orders.map(order => `
        <tr>
            <td>#${order.order_id}</td>
            <td>${order.customer_name || 'N/A'}</td>
            <td>${formatDate(order.order_date)}</td>
            <td>$${order.total_amount.toFixed(2)}</td>
            <td>
                <span class="status-badge ${order.status.toLowerCase()}">
                    ${order.status}
                </span>
            </td>
            <td>
                <div class="action-buttons">
                    <button class="action-btn edit" onclick="viewOrder(${order.order_id})" title="View">
                        <i class="fas fa-eye"></i>
                    </button>
                    <button class="action-btn delete" onclick="deleteOrder(${order.order_id})" title="Delete">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </td>
        </tr>
    `).join('');
}

async function filterOrders() {
    currentPage = 1;
    await loadOrders(currentPage);
}

// Modal functions
function showModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.classList.add('show');
    document.body.style.overflow = 'hidden';
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.classList.remove('show');
    document.body.style.overflow = 'auto';
    
    // Reset form if exists
    const form = modal.querySelector('form');
    if (form) form.reset();
}

function showAddProductModal() {
    showModal('add-product-modal');
}

function showAddOrderModal() {
    showModal('add-order-modal');
    loadProductsForOrder();
}

function showAddSupplierModal() {
    showModal('add-supplier-modal');
}

// Form handlers
async function handleAddProduct(e) {
    e.preventDefault();
    
    try {
        const formData = new FormData(e.target);
        const productData = {
            product_name: document.getElementById('product-name').value,
            sku: document.getElementById('product-sku').value,
            description: document.getElementById('product-description').value,
            category_id: document.getElementById('product-category').value || null,
            supplier_id: document.getElementById('product-supplier').value || null,
            unit_price: parseFloat(document.getElementById('product-price').value),
            stock_level: parseInt(document.getElementById('product-stock').value) || 0,
            reorder_level: parseInt(document.getElementById('product-reorder').value) || 10
        };

        await apiCall('/products', {
            method: 'POST',
            body: JSON.stringify(productData)
        });

        showToast('Product added successfully', 'success');
        closeModal('add-product-modal');
        
        if (currentSection === 'products') {
            loadProducts();
        }
        loadDashboardStats();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

async function handleAddOrder(e) {
    e.preventDefault();
    
    try {
        const orderItems = [];
        const itemElements = document.querySelectorAll('.order-item');
        
        for (const item of itemElements) {
            const productId = item.querySelector('.order-product').value;
            const quantity = parseInt(item.querySelector('.order-quantity').value);
            const unitPrice = parseFloat(item.querySelector('.order-unit-price').value);
            
            if (productId && quantity && unitPrice) {
                orderItems.push({
                    product_id: parseInt(productId),
                    quantity: quantity,
                    unit_price: unitPrice
                });
            }
        }

        if (orderItems.length === 0) {
            showToast('Please add at least one item to the order', 'error');
            return;
        }

        const orderData = {
            customer_name: document.getElementById('order-customer-name').value,
            customer_email: document.getElementById('order-customer-email').value,
            delivery_date: document.getElementById('order-delivery-date').value,
            items: orderItems
        };

        await apiCall('/orders', {
            method: 'POST',
            body: JSON.stringify(orderData)
        });

        showToast('Order created successfully', 'success');
        closeModal('add-order-modal');
        
        if (currentSection === 'orders') {
            loadOrders();
        }
        loadDashboardStats();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

async function handleAddSupplier(e) {
    e.preventDefault();
    
    try {
        const supplierData = {
            supplier_name: document.getElementById('supplier-name').value,
            contact_person: document.getElementById('supplier-contact').value,
            email: document.getElementById('supplier-email').value,
            phone: document.getElementById('supplier-phone').value,
            address: document.getElementById('supplier-address').value,
            city: document.getElementById('supplier-city').value,
            country: document.getElementById('supplier-country').value
        };

        await apiCall('/suppliers', {
            method: 'POST',
            body: JSON.stringify(supplierData)
        });

        showToast('Supplier added successfully', 'success');
        closeModal('add-supplier-modal');
        
        if (currentSection === 'suppliers') {
            loadSuppliers();
        }
        loadSuppliers(); // Refresh dropdown
    } catch (error) {
        showToast(error.message, 'error');
    }
}

// Order item management
function addOrderItem() {
    const container = document.getElementById('order-items');
    const newItem = document.createElement('div');
    newItem.className = 'order-item';
    newItem.innerHTML = `
        <div class="form-row">
            <div class="form-group">
                <label>Product</label>
                <select class="order-product" required>
                    <option value="">Select Product</option>
                </select>
            </div>
            <div class="form-group">
                <label>Quantity</label>
                <input type="number" class="order-quantity" min="1" required>
            </div>
            <div class="form-group">
                <label>Unit Price</label>
                <input type="number" class="order-unit-price" step="0.01" min="0" readonly>
            </div>
            <div class="form-group">
                <label>Total</label>
                <input type="number" class="order-total" step="0.01" readonly>
            </div>
            <div class="form-group">
                <button type="button" class="btn btn-danger btn-sm" onclick="removeOrderItem(this)">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        </div>
    `;
    
    container.appendChild(newItem);
    loadProductsForOrderItem(newItem);
    setupOrderItemListeners(newItem);
}

function removeOrderItem(button) {
    const orderItem = button.closest('.order-item');
    orderItem.remove();
    updateOrderTotal();
}

async function loadProductsForOrder() {
    try {
        const data = await apiCall('/products?per_page=1000');
        const productSelects = document.querySelectorAll('.order-product');
        
        productSelects.forEach(select => {
            select.innerHTML = '<option value="">Select Product</option>';
            data.products.forEach(product => {
                select.innerHTML += `<option value="${product.product_id}" data-price="${product.unit_price}">${product.product_name} (Stock: ${product.stock_level})</option>`;
            });
        });
        
        setupOrderItemListeners();
    } catch (error) {
        showToast('Error loading products for order', 'error');
    }
}

function loadProductsForOrderItem(item) {
    const select = item.querySelector('.order-product');
    select.innerHTML = '<option value="">Select Product</option>';
    
    if (products.length === 0) {
        // Load products if not already loaded
        apiCall('/products?per_page=1000').then(data => {
            data.products.forEach(product => {
                select.innerHTML += `<option value="${product.product_id}" data-price="${product.unit_price}">${product.product_name} (Stock: ${product.stock_level})</option>`;
            });
        });
    } else {
        products.forEach(product => {
            select.innerHTML += `<option value="${product.product_id}" data-price="${product.unit_price}">${product.product_name} (Stock: ${product.stock_level})</option>`;
        });
    }
}

function setupOrderItemListeners(container = document) {
    const productSelects = container.querySelectorAll('.order-product');
    const quantityInputs = container.querySelectorAll('.order-quantity');
    
    productSelects.forEach(select => {
        select.addEventListener('change', function() {
            const selectedOption = this.options[this.selectedIndex];
            const price = selectedOption.dataset.price || 0;
            const priceInput = this.closest('.order-item').querySelector('.order-unit-price');
            priceInput.value = price;
            updateItemTotal(this.closest('.order-item'));
        });
    });
    
    quantityInputs.forEach(input => {
        input.addEventListener('input', function() {
            updateItemTotal(this.closest('.order-item'));
        });
    });
}

function updateItemTotal(item) {
    const quantity = parseFloat(item.querySelector('.order-quantity').value) || 0;
    const unitPrice = parseFloat(item.querySelector('.order-unit-price').value) || 0;
    const total = quantity * unitPrice;
    
    item.querySelector('.order-total').value = total.toFixed(2);
    updateOrderTotal();
}

function updateOrderTotal() {
    const totals = document.querySelectorAll('.order-total');
    let grandTotal = 0;
    
    totals.forEach(total => {
        grandTotal += parseFloat(total.value) || 0;
    });
    
    document.getElementById('order-grand-total').textContent = grandTotal.toFixed(2);
}

// Reports functions
async function loadLowInventoryReport() {
    try {
        showLoading();
        const data = await apiCall('/reports/low-inventory');
        
        const content = document.getElementById('report-content');
        content.innerHTML = `
            <h2>Low Inventory Report</h2>
            <p>Items that need to be reordered (${data.total_items} items)</p>
            <div class="table-container">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Product</th>
                            <th>SKU</th>
                            <th>Category</th>
                            <th>Current Stock</th>
                            <th>Reorder Level</th>
                            <th>Shortage</th>
                            <th>Supplier</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.low_inventory_items.map(item => `
                            <tr>
                                <td>${item.product_name}</td>
                                <td>${item.sku || 'N/A'}</td>
                                <td>${item.category_name || 'N/A'}</td>
                                <td>${item.stock_level}</td>
                                <td>${item.reorder_level}</td>
                                <td>${item.shortage_quantity}</td>
                                <td>${item.supplier_name || 'N/A'}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
        
        hideLoading();
    } catch (error) {
        showToast('Error loading low inventory report', 'error');
        hideLoading();
    }
}

async function loadSalesByCategoryReport() {
    try {
        showLoading();
        const data = await apiCall('/reports/sales-by-category');
        
        const content = document.getElementById('report-content');
        content.innerHTML = `
            <h2>Sales by Category Report</h2>
            <p>Performance analysis by product category</p>
            <div class="table-container">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Category</th>
                            <th>Products Sold</th>
                            <th>Total Quantity</th>
                            <th>Total Revenue</th>
                            <th>Avg Price</th>
                            <th>Orders</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.sales_by_category.map(category => `
                            <tr>
                                <td>${category.category_name}</td>
                                <td>${category.products_sold}</td>
                                <td>${category.total_quantity_sold}</td>
                                <td>$${category.total_revenue.toFixed(2)}</td>
                                <td>$${category.avg_selling_price.toFixed(2)}</td>
                                <td>${category.number_of_orders}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
        
        hideLoading();
    } catch (error) {
        showToast('Error loading sales by category report', 'error');
        hideLoading();
    }
}

async function loadTopProductsReport() {
    try {
        showLoading();
        const data = await apiCall('/reports/top-selling-products?limit=20');
        
        const content = document.getElementById('report-content');
        content.innerHTML = `
            <h2>Top Selling Products</h2>
            <p>Best performing products by sales volume</p>
            <div class="table-container">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Product</th>
                            <th>SKU</th>
                            <th>Category</th>
                            <th>Total Sold</th>
                            <th>Revenue</th>
                            <th>Current Stock</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.top_selling_products.map(product => `
                            <tr>
                                <td>${product.product_name}</td>
                                <td>${product.sku || 'N/A'}</td>
                                <td>${product.category_name}</td>
                                <td>${product.total_sold}</td>
                                <td>$${product.total_revenue.toFixed(2)}</td>
                                <td>${product.current_stock}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
        
        hideLoading();
    } catch (error) {
        showToast('Error loading top products report', 'error');
        hideLoading();
    }
}

async function loadInventoryValuationReport() {
    try {
        showLoading();
        const data = await apiCall('/reports/inventory-valuation');
        
        const content = document.getElementById('report-content');
        content.innerHTML = `
            <h2>Inventory Valuation Report</h2>
            <p>Current inventory value by category</p>
            <div class="table-container">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Category</th>
                            <th>Product Count</th>
                            <th>Total Units</th>
                            <th>Total Value</th>
                            <th>Avg Unit Price</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${data.inventory_valuation.map(category => `
                            <tr>
                                <td>${category.category_name}</td>
                                <td>${category.product_count}</td>
                                <td>${category.total_units}</td>
                                <td>$${category.total_value.toFixed(2)}</td>
                                <td>$${category.avg_unit_price.toFixed(2)}</td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>
            </div>
        `;
        
        hideLoading();
    } catch (error) {
        showToast('Error loading inventory valuation report', 'error');
        hideLoading();
    }
}

// CRUD operations
async function editProduct(productId) {
    // Implementation for editing products
    showToast('Edit functionality coming soon', 'info');
}

async function deleteProduct(productId) {
    if (!confirm('Are you sure you want to delete this product?')) return;
    
    try {
        await apiCall(`/products/${productId}`, { method: 'DELETE' });
        showToast('Product deleted successfully', 'success');
        loadProducts();
        loadDashboardStats();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

async function editSupplier(supplierId) {
    showToast('Edit functionality coming soon', 'info');
}

async function deleteSupplier(supplierId) {
    if (!confirm('Are you sure you want to delete this supplier?')) return;
    
    try {
        await apiCall(`/suppliers/${supplierId}`, { method: 'DELETE' });
        showToast('Supplier deleted successfully', 'success');
        loadSuppliers();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

async function viewOrder(orderId) {
    showToast('Order details view coming soon', 'info');
}

async function deleteOrder(orderId) {
    if (!confirm('Are you sure you want to delete this order?')) return;
    
    try {
        await apiCall(`/orders/${orderId}`, { method: 'DELETE' });
        showToast('Order deleted successfully', 'success');
        loadOrders();
        loadDashboardStats();
    } catch (error) {
        showToast(error.message, 'error');
    }
}

// Utility functions
function renderPagination(containerId, currentPage, totalPages, loadFunction) {
    const container = document.getElementById(containerId);
    if (!container || totalPages <= 1) {
        if (container) container.innerHTML = '';
        return;
    }

    let pagination = '';
    
    // Previous button
    pagination += `<button ${currentPage === 1 ? 'disabled' : ''} onclick="${loadFunction.name}(${currentPage - 1})">Previous</button>`;
    
    // Page numbers
    for (let i = Math.max(1, currentPage - 2); i <= Math.min(totalPages, currentPage + 2); i++) {
        pagination += `<button class="${i === currentPage ? 'active' : ''}" onclick="${loadFunction.name}(${i})">${i}</button>`;
    }
    
    // Next button
    pagination += `<button ${currentPage === totalPages ? 'disabled' : ''} onclick="${loadFunction.name}(${currentPage + 1})">Next</button>`;
    
    container.innerHTML = pagination;
}

function formatDate(dateString) {
    if (!dateString) return 'N/A';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

function showLoading() {
    document.getElementById('loading').classList.add('show');
}

function hideLoading() {
    document.getElementById('loading').classList.remove('show');
}

function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <div style="display: flex; align-items: center; gap: 0.5rem;">
            <i class="fas fa-${getToastIcon(type)}"></i>
            <span>${message}</span>
        </div>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 5000);
}

function getToastIcon(type) {
    switch (type) {
        case 'success': return 'check-circle';
        case 'error': return 'exclamation-circle';
        case 'warning': return 'exclamation-triangle';
        default: return 'info-circle';
    }
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

