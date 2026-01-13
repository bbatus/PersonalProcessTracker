"""
Seed default categories
"""

from app.core.database import SessionLocal
from app.models.category import Category, DEFAULT_CATEGORIES

def seed_categories():
    db = SessionLocal()
    
    try:
        # Check if categories already exist
        existing_count = db.query(Category).count()
        
        if existing_count > 0:
            print(f"✅ Categories already seeded ({existing_count} categories exist)")
            return
        
        # Create default categories
        for cat_data in DEFAULT_CATEGORIES:
            category = Category(
                name=cat_data["name"],
                color=cat_data["color"]
            )
            db.add(category)
        
        db.commit()
        print(f"✅ Seeded {len(DEFAULT_CATEGORIES)} default categories")
        
        # List categories
        categories = db.query(Category).all()
        for cat in categories:
            print(f"   - {cat.name} ({cat.color})")
        
    except Exception as e:
        print(f"❌ Error seeding categories: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_categories()
