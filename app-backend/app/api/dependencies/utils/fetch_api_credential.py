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

    # Check the role of the account
    if account.role == "main":
        # If the account is a main account, return its API credentials
        return {"main_api_key": account.api_key, "main_api_secret": account.api_secret}
    elif "sub" in account.role:
        # If the account is a sub account, fetch the main account's credentials
        main_account = db.query(Account).filter(Account.role == "main").first()
        if not main_account:
            raise ValueError(
                f"Main account for sub-account '{account_name}' not found."
            )
        if not main_account.is_activate:
            raise ValueError(
                f"Main account for sub-account '{account_name}' is deactivated."
            )

        # Return both the main account's and sub account's API credentials
        return {
            "main_api_key": main_account.api_key,
            "main_api_secret": main_account.api_secret,
            "api_key": account.api_key,
            "api_secret": account.api_secret,
        }
    else:
        raise ValueError(f"Unknown role '{account.role}' for account '{account_name}'.")
