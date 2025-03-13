from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.pydantic_schemas import AccountCreate, AccountResponse, AccountUpdate
from app.api.dependencies.accounts import create_account, update_account
from app.core.db_session import get_db
from app.models.db_models import Account

acc_router = APIRouter(prefix="/accounts", tags=["Accounts"])

# route to create an account
@acc_router.post("/create-account", response_model=AccountResponse)
def create_new_account(account: AccountCreate, db: Session = Depends(get_db)):
    """Creates a new account and stores it in the database."""
    existing_account = db.query(Account).filter(Account.account_name == account.account_name).first()
    if existing_account:
        raise HTTPException(status_code=400, detail="Account name already exists")
    
    return create_account(db, account)


# route to get all the accounts
@acc_router.get("/get-accounts", response_model=list[AccountResponse])
def get_all_accounts(db: Session = Depends(get_db)):
    """Retrieves all accounts from the database and returns them as a list."""
    accounts = db.query(Account).all()
    if not accounts:
        raise HTTPException(status_code=404, detail="No accounts found")
    return accounts

# route to update details of the account
@acc_router.put("/update-account/{acc_id}", response_model=AccountResponse)
def update_acc_details(acc_id: int, acc_update : AccountUpdate, db: Session = Depends(get_db)):
    return update_account(db, acc_id, acc_update)