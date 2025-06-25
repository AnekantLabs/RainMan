# some utility functions where we might query the db

from sqlalchemy.orm import Session
from app.models.db_models import Account


def fetch_api_credentials(db: Session, account_name: str):
    """
    Fetches API credentials for the given account from the database.
    Only returns credentials if the account is active and not soft-deleted.
    """

    print(f"Fetching API credentials for account: {account_name}")

    # Fetch the requested account (non-deleted & active)
    account = db.query(Account).filter(
        Account.account_name == account_name,
        Account.is_activate == True,
        Account.is_deleted == False
    ).first()

    if not account:
        raise ValueError(f"Active account with name '{account_name}' not found.")

    if account.role == "main":
        return {
            "main_api_key": account.api_key,
            "main_api_secret": account.api_secret
        }

    elif "sub" in account.role:
        # Fetch active, non-deleted main account
        main_account = db.query(Account).filter(
            Account.role == "main",
            Account.is_activate == True,
            Account.is_deleted == False
        ).first()

        if not main_account:
            raise ValueError(f"Active main account for sub-account '{account_name}' not found.")

        return {
            "main_api_key": main_account.api_key,
            "main_api_secret": main_account.api_secret,
            "api_key": account.api_key,
            "api_secret": account.api_secret,
            "role": account.role
        }

    else:
        raise ValueError(f"Unknown role '{account.role}' for account '{account_name}'.")
