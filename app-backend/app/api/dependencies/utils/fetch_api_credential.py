# some utility functions where we might query the db

from sqlalchemy.orm import Session
from app.models.db_models import Account

def fetch_api_credentials(db: Session, account_name: str):
    """
    Fetches API credentials for the given account from the database.
    """
    
    print(f"Fetching API credentials for account: {account_name}")
    # Check if the account exists and is activated
    # query the account table from the db
    # filter the account by account_name and check if it is activated
    account = db.query(Account).filter(Account.account_name == account_name).first()
    if not account:
        raise ValueError(f"Account with name '{account_name}' not found.")
    if not account.is_activate:
        raise ValueError(f"Account '{account_name}' is deactivated.")
    
    # if account is active and found, return the api key and secret
    return {
        "api_key": account.api_key,
        "api_secret": account.api_secret
    }