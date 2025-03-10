from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.pydantic_schemas import AccountCreate, AccountResponse
from app.api.dependencies.accounts import create_user
from app.core.db_session import get_db
from app.models.db_models import Account

acc_router = APIRouter(prefix="/users", tags=["Users"])

@acc_router.post("/create-user", response_model=AccountResponse)
def create_new_user(account: AccountCreate, db: Session = Depends(get_db)):
    """Creates a new user and stores it in the database."""
    existing_user = db.query(Account).filter(account.account_name == Account.account_name).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Account name already exists")
    
    return create_user(db, account)
