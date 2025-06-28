from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from app.schemas.pydantic_schemas import AccountCreate, AccountResponse, AccountUpdate
from app.api.dependencies.accounts import create_account, update_account
from app.core.db_session import get_db
from app.models.db_models import Account
from app.celery.celery_app import celery
from pybit.unified_trading import HTTP
from concurrent.futures import ThreadPoolExecutor, as_completed

acc_router = APIRouter(prefix="/accounts", tags=["Accounts"])

# Create new account
@acc_router.post("/create-account", response_model=AccountResponse)
def create_new_account(account: AccountCreate, db: Session = Depends(get_db)):
    existing_account = db.query(Account).filter(
        Account.account_name == account.account_name,
        Account.is_deleted == False
    ).first()
    if existing_account:
        raise HTTPException(status_code=400, detail="Account name already exists")
    return create_account(db, account)


# Get all non-deleted accounts
@acc_router.get("/get-accounts", response_model=list[AccountResponse])
def get_all_accounts(db: Session = Depends(get_db)):
    accounts = db.query(Account).filter(Account.is_deleted == False).all()
    if not accounts:
        raise HTTPException(status_code=404, detail="No accounts found")
    return accounts

# Get accounts with wallet info
@acc_router.get("/get-account-info")
def get_account_info(db: Session = Depends(get_db)):
    accounts = db.query(Account).filter(Account.is_deleted == False).all()
    if not accounts:
        raise HTTPException(status_code=404, detail="No accounts found")

    def fetch_account_with_wallet(account):
        try:
            session = HTTP(
                testnet=True,
                api_key=account.api_key,
                api_secret=account.api_secret,
            )
            response = session.get_wallet_balance(accountType="UNIFIED")
            wallet_data = response["result"]["list"][0]
            wallet_info = {
                "total_wallet_balance": wallet_data.get("totalWalletBalance"),
                "total_available_balance": wallet_data.get("totalAvailableBalance"),
                "total_margin_balance": wallet_data.get("totalMarginBalance"),
                "total_equity": wallet_data.get("totalEquity"),
                "coins": wallet_data.get("coin", []),
            }
        except Exception as e:
            wallet_info = {"error": str(e)}

        return {
            "id": account.id,
            "account_name": account.account_name,
            "api_key": account.api_key,
            "api_secret": account.api_secret,
            "is_activate": account.is_activate,
            "wallet_info": wallet_info,
        }

    results = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_account = {executor.submit(fetch_account_with_wallet, acc): acc for acc in accounts}
        for future in as_completed(future_to_account):
            results.append(future.result())

    return JSONResponse(content={"accounts": results})

# Update account details (skip deleted ones)
@acc_router.put("/update-account/{acc_id}", response_model=AccountResponse)
def update_acc_details(acc_id: int, acc_update: AccountUpdate, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == acc_id, Account.is_deleted == False).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found or is deleted")
    return update_account(db, acc_id, acc_update)


@acc_router.post("/send-accounts-to-queue")
def send_accounts_to_queue(db: Session = Depends(get_db)):
    active_accounts = db.query(Account).filter(
        Account.is_activate == True,
        Account.is_deleted == False
    ).all()
    if not active_accounts:
        raise HTTPException(status_code=404, detail="No active accounts found")

    accounts_data = {
        account.account_name: {
            "api_key": account.api_key,
            "api_secret": account.api_secret,
        }
        for account in active_accounts
    }

    celery.send_task("tasks.connect_websocket", args=[accounts_data], queue="websocket_queue")
    return {"message": f"Sent {len(accounts_data)} active accounts to the queue"}


# Soft-delete account
@acc_router.delete("/delete-account/{acc_id}")
def delete_account(acc_id: int, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == acc_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    if account.is_deleted:
        return {"message": f"Account with ID {acc_id} is already deleted"}

    account.is_deleted = True
    db.commit()
    return {"message": f"Account with ID {acc_id} has been marked as deleted"}