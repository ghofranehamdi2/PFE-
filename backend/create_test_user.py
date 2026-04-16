import sys
import os

# Add parent directory to path to import app
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.crud import crud
from app.schemas import schemas

def create_user():
    db = SessionLocal()
    try:
        user_in = schemas.UserCreate(
            email="user@example.com",
            password="password123",
            full_name="Test User"
        )
        user = crud.user.get_by_email(db, email=user_in.email)
        if not user:
            crud.user.create(db, obj_in=user_in)
            print(f"User {user_in.email} created successfully.")
        else:
            print(f"User {user_in.email} already exists.")
    finally:
        db.close()

if __name__ == "__main__":
    create_user()
