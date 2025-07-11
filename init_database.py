#!/usr/bin/env python3
"""
Database initialization script for Inventory Control System
This script creates the database tables and populates them with sample data
"""

import os
import sys
import sqlite3
from pathlib import Path

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def init_database():
    """Initialize the database with schema and sample data"""
    
    # Database file path
    db_path = os.path.join(os.path.dirname(__file__), 'src', 'database', 'app.db')
    
    # Ensure database directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # Remove existing database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"Removed existing database: {db_path}")
    
    # Connect to database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Read and execute schema
        schema_path = os.path.join(os.path.dirname(__file__), 'database_schema.sql')
        with open(schema_path, 'r') as f:
            schema_sql = f.read()
        
        # Execute schema statements
        cursor.executescript(schema_sql)
        print("Database schema created successfully")
        
        # Read and execute sample data
        sample_data_path = os.path.join(os.path.dirname(__file__), 'sample_data.sql')
        with open(sample_data_path, 'r') as f:
            sample_data_sql = f.read()
        
        # Execute sample data statements
        cursor.executescript(sample_data_sql)
        print("Sample data inserted successfully")
        
        # Commit changes
        conn.commit()
        print(f"Database initialized successfully at: {db_path}")
        
        # Print some statistics
        cursor.execute("SELECT COUNT(*) FROM categories")
        categories_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM suppliers")
        suppliers_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM products")
        products_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM orders")
        orders_count = cursor.fetchone()[0]
        
        print(f"\nDatabase Statistics:")
        print(f"- Categories: {categories_count}")
        print(f"- Suppliers: {suppliers_count}")
        print(f"- Products: {products_count}")
        print(f"- Orders: {orders_count}")
        
    except Exception as e:
        print(f"Error initializing database: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

if __name__ == "__main__":
    init_database()

