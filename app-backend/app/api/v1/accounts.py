from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.pydantic_schemas import AccountCreate, AccountResponse
from app.api.dependencies.accounts import create_account
from app.core.db_session import get_db
from app.models.db_models import Account

acc_router = APIRouter(prefix="/accounts", tags=["Accounts"])

@acc_router.post("/create-account", response_model=AccountResponse)
def create_new_account(account: AccountCreate, db: Session = Depends(get_db)):
    """Creates a new account and stores it in the database."""
    existing_account = db.query(Account).filter(Account.account_name == account.account_name).first()
    if existing_account:
        raise HTTPException(status_code=400, detail="Account name already exists")
    
    return create_account(db, account)
