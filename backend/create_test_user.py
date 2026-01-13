"""
Create a test user for testing services
"""

from app.core.database import SessionLocal
from app.models.user import User
from app.utils.password import hash_password
import uuid

def create_test_user():
    db = SessionLocal()
    
    try:
        # Check if test user exists
        existing = db.query(User).filter(User.email == "test@example.com").first()
        if existing:
            print(f"✅ Test user already exists: {existing.email} ({existing.id})")
            return
        
        # Create test user
        user = User(
            username="testuser",
            email="test@example.com",
            password_hash=hash_password("Test123!"),
            email_verified=True,
            timezone="UTC"
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        print(f"✅ Test user created: {user.email} ({user.id})")
        print(f"   Username: {user.username}")
        print(f"   Password: Test123!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_test_user()
