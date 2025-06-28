# controller for account routes
from sqlalchemy.orm import Session
from app.models.db_models import Account
from app.schemas.pydantic_schemas import AccountCreate, AccountUpdate


def create_account(db: Session, account_data: AccountCreate):
    """Handles account creation logic."""
    new_account = Account(**account_data.dict())
    db.add(new_account)
    db.commit()
    db.refresh(new_account)
    return new_account


def update_account(db: Session, acc_id: int, account_update: AccountUpdate):
    """Updates an account in the database, only if it's not soft-deleted."""
    
    # Fetch the account by ID and ensure it's not deleted
    account = db.query(Account).filter(
        Account.id == acc_id,
        Account.is_deleted == False
    ).first()

    if not account:
        raise ValueError(f"Account with ID '{acc_id}' not found or has been deleted.")

    # Update fields
    account.account_name = account_update.account_name
    account.role = account_update.role
    account.api_key = account_update.api_key
    account.api_secret = account_update.api_secret
    account.risk_percentage = account_update.risk_percentage
    account.leverage = account_update.leverage
    account.is_activate = account_update.is_activate

    # Commit and return updated record
    db.commit()
    db.refresh(account)
    return account
