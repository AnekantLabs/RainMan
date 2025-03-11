
# controller for account routes
from sqlalchemy.orm import Session
from app.models.db_models import Account
from app.schemas.pydantic_schemas import AccountCreate

def create_account(db: Session, account_data: AccountCreate):
    """Handles account creation logic."""
    new_account = Account(**account_data.dict())
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return new_account
