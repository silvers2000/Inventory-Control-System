# Inventory Control System

A comprehensive web-based inventory management system built with Flask backend and modern HTML/CSS/JavaScript frontend.

## Features

### Core Functionality
- **Product Management**: Add, edit, delete, and search products with categories and suppliers
- **Order Management**: Create and track customer orders with automatic stock updates
- **Supplier Management**: Maintain supplier information and contact details
- **Inventory Tracking**: Real-time stock level monitoring with low-stock alerts
- **Reporting & Analytics**: Comprehensive reports including:
  - Low inventory items requiring reordering
  - Sales performance by category
  - Top selling products
  - Inventory valuation by category
  - Dashboard with key metrics

### Technical Features
- **Database**: SQLite with comprehensive schema including triggers for automatic stock updates
- **API**: RESTful API endpoints for all CRUD operations
- **Frontend**: Responsive design with modern UI/UX
- **Real-time Updates**: Automatic stock level adjustments when orders are placed
- **Search & Filtering**: Advanced search and filtering capabilities
- **Pagination**: Efficient data loading with pagination support

## Database Schema

The system uses a well-designed relational database with the following entities:

### Core Tables
- **Categories**: Product categorization
- **Suppliers**: Supplier information and contact details
- **Products**: Product catalog with pricing and stock information
- **Orders**: Customer order management
- **Order Items**: Individual items within orders
- **Purchase Orders**: Orders from suppliers
- **Purchase Order Items**: Items within purchase orders
- **Inventory Transactions**: Complete audit trail of stock movements

### Key Features
- **Automatic Triggers**: Stock levels update automatically when orders are placed
- **Data Integrity**: Foreign key constraints ensure data consistency
- **Audit Trail**: Complete transaction history for inventory movements
- **Performance**: Optimized indexes for fast queries

## API Endpoints

### Products
- `GET /api/products` - List products with filtering and pagination
- `POST /api/products` - Create new product
- `GET /api/products/{id}` - Get specific product
- `PUT /api/products/{id}` - Update product
- `DELETE /api/products/{id}` - Delete product
- `POST /api/products/{id}/adjust-stock` - Manual stock adjustment
- `GET /api/products/low-stock` - Get low stock items

### Orders
- `GET /api/orders` - List orders with filtering
- `POST /api/orders` - Create new order
- `GET /api/orders/{id}` - Get specific order
- `PUT /api/orders/{id}` - Update order
- `DELETE /api/orders/{id}` - Delete order
- `PUT /api/orders/{id}/status` - Update order status
- `GET /api/orders/stats` - Order statistics

### Suppliers
- `GET /api/suppliers` - List suppliers
- `POST /api/suppliers` - Create new supplier
- `GET /api/suppliers/{id}` - Get specific supplier
- `PUT /api/suppliers/{id}` - Update supplier
- `DELETE /api/suppliers/{id}` - Delete supplier

### Purchase Orders
- `GET /api/purchase-orders` - List purchase orders
- `POST /api/purchase-orders` - Create new purchase order
- `GET /api/purchase-orders/{id}` - Get specific purchase order
- `PUT /api/purchase-orders/{id}` - Update purchase order
- `POST /api/purchase-orders/{id}/receive` - Mark as received
- `DELETE /api/purchase-orders/{id}` - Delete purchase order

### Reports
- `GET /api/reports/low-inventory` - Low inventory report
- `GET /api/reports/sales-by-category` - Sales by category report
- `GET /api/reports/product-performance` - Product performance report
- `GET /api/reports/monthly-sales` - Monthly sales report
- `GET /api/reports/inventory-valuation` - Inventory valuation report
- `GET /api/reports/top-selling-products` - Top selling products
- `GET /api/reports/recent-transactions` - Recent transactions
- `GET /api/reports/dashboard-stats` - Dashboard statistics

### Categories
- `GET /api/categories` - List categories
- `POST /api/categories` - Create new category

## Installation & Setup

### Prerequisites
- Python 3.11+
- Virtual environment support

### Local Development Setup

1. **Clone/Extract the project**
   ```bash
   cd inventory_system
   ```

2. **Activate virtual environment**
   ```bash
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize database**
   ```bash
   python init_database.py
   ```

5. **Start the application**
   ```bash
   python src/main.py
   ```

6. **Access the application**
   Open your browser and navigate to `http://localhost:5000`

### Production Deployment

The application is ready for production deployment with:
- CORS enabled for cross-origin requests
- Proper error handling and validation
- Secure database operations
- Responsive design for mobile and desktop

## Sample Data

The system comes pre-loaded with sample data including:
- **5 Categories**: Electronics, Office Supplies, Furniture, Clothing, Books
- **5 Suppliers**: Various suppliers with complete contact information
- **25 Products**: Diverse product catalog across all categories
- **4 Sample Orders**: Orders in different statuses (Pending, Processing, Shipped, Delivered)

## Business Logic

### Inventory Management
- **Automatic Stock Updates**: When orders are placed, stock levels are automatically reduced
- **Low Stock Alerts**: Products below reorder level are flagged for attention
- **Purchase Order Integration**: Receiving purchase orders automatically increases stock
- **Transaction Logging**: All stock movements are logged for audit purposes

### Order Processing
- **Stock Validation**: Orders cannot be placed if insufficient stock is available
- **Order Status Tracking**: Orders progress through defined statuses
- **Cancellation Handling**: Cancelled orders restore stock levels
- **Total Calculation**: Order totals are automatically calculated

### Reporting
- **Real-time Analytics**: All reports reflect current data
- **Performance Metrics**: Track sales performance and inventory turnover
- **Financial Insights**: Revenue tracking and inventory valuation
- **Operational Reports**: Low stock alerts and reorder recommendations

## User Interface

### Dashboard
- Key performance indicators (KPIs)
- Quick action buttons
- Recent transaction history
- Visual status indicators

### Product Management
- Comprehensive product listing with search and filters
- Category and supplier filtering
- Stock level indicators
- Bulk operations support

### Order Management
- Order creation with product selection
- Status tracking and updates
- Customer information management
- Order history and details

### Supplier Management
- Supplier directory with contact information
- Purchase order integration
- Performance tracking

### Reports & Analytics
- Interactive report selection
- Detailed data tables
- Export capabilities
- Visual indicators and status badges

## Security Features

- Input validation and sanitization
- SQL injection prevention through parameterized queries
- Error handling with appropriate user feedback
- Data integrity constraints
- Transaction rollback on errors

## Performance Optimizations

- Database indexing for fast queries
- Pagination for large datasets
- Efficient API design with minimal data transfer
- Responsive frontend with smooth animations
- Optimized database queries with joins

## Browser Compatibility

The application is tested and compatible with:
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Future Enhancements

Potential areas for expansion:
- Barcode scanning integration
- Multi-location inventory support
- Advanced reporting with charts and graphs
- Email notifications for low stock
- Integration with accounting systems
- Mobile app development
- Advanced user roles and permissions

## Support

For technical support or questions about the system, refer to the code documentation and API endpoints listed above. The system is designed to be self-documenting with clear error messages and intuitive user interface.

