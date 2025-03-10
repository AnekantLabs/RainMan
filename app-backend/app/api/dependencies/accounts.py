
# controller for account routes
from sqlalchemy.orm import Session
from app.models.db_models import User
from app.schemas.pydantic_schemas import UserCreate

def create_user(db: Session, user_data: UserCreate):
    """Handles user creation logic."""
    new_user = User(**user_data.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user
