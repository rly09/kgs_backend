import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from app.database import SessionLocal, engine, Base
from app.models import Admin, Category, Product, Settings
from app.auth import get_password_hash
from datetime import datetime

def seed_database():
    """Seed the database with initial data"""
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_admin = db.query(Admin).first()
        if existing_admin:
            print("Database already seeded. Skipping...")
            return
        
        print("Seeding database...")
        
        # Create default admin
        admin = Admin(
            phone="9999999999",
            password_hash=get_password_hash("admin123"),
            name="Admin",
            created_at=datetime.utcnow()
        )
        db.add(admin)
        print("✓ Created default admin (phone: 9999999999, password: admin123)")
        
        # Create categories
        categories_data = [
            "Groceries",
            "Snacks",
            "Beverages",
            "Household",
            "Personal Care"
        ]
        
        categories = {}
        for cat_name in categories_data:
            category = Category(name=cat_name, created_at=datetime.utcnow())
            db.add(category)
            db.flush()
            categories[cat_name] = category.id
        print(f"✓ Created {len(categories_data)} categories")
        
        # Create sample products
        products_data = [
            # Groceries
            {"name": "Rice (1kg)", "category": "Groceries", "price": 60.0, "stock": 50},
            {"name": "Wheat Flour (1kg)", "category": "Groceries", "price": 45.0, "stock": 40},
            {"name": "Sugar (1kg)", "category": "Groceries", "price": 50.0, "stock": 30},
            {"name": "Cooking Oil (1L)", "category": "Groceries", "price": 150.0, "stock": 25},
            {"name": "Dal (1kg)", "category": "Groceries", "price": 120.0, "stock": 35},
            
            # Snacks
            {"name": "Chips", "category": "Snacks", "price": 20.0, "stock": 100},
            {"name": "Biscuits", "category": "Snacks", "price": 30.0, "stock": 80},
            {"name": "Namkeen", "category": "Snacks", "price": 25.0, "stock": 60},
            {"name": "Chocolate", "category": "Snacks", "price": 40.0, "stock": 50},
            
            # Beverages
            {"name": "Tea (250g)", "category": "Beverages", "price": 80.0, "stock": 40},
            {"name": "Coffee (100g)", "category": "Beverages", "price": 120.0, "stock": 30},
            {"name": "Soft Drink (1L)", "category": "Beverages", "price": 40.0, "stock": 60},
            {"name": "Juice (1L)", "category": "Beverages", "price": 60.0, "stock": 45},
            
            # Household
            {"name": "Detergent (1kg)", "category": "Household", "price": 150.0, "stock": 25},
            {"name": "Soap", "category": "Household", "price": 30.0, "stock": 70},
            {"name": "Toothpaste", "category": "Household", "price": 50.0, "stock": 55},
            
            # Personal Care
            {"name": "Shampoo (200ml)", "category": "Personal Care", "price": 120.0, "stock": 30},
            {"name": "Face Wash", "category": "Personal Care", "price": 80.0, "stock": 40},
        ]
        
        for prod_data in products_data:
            product = Product(
                name=prod_data["name"],
                category_id=categories[prod_data["category"]],
                price=prod_data["price"],
                stock=prod_data["stock"],
                is_available=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.add(product)
        print(f"✓ Created {len(products_data)} sample products")
        
        # Create default settings
        discount_setting = Settings(
            key="discount_percentage",
            value="0",
            updated_at=datetime.utcnow()
        )
        db.add(discount_setting)
        print("✓ Created default settings (discount: 0%)")
        
        db.commit()
        print("\n✅ Database seeded successfully!")
        print("\nDefault Admin Credentials:")
        print("  Phone: 9999999999")
        print("  Password: admin123")
        
    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
