from fastapi import APIRouter, Depends, HTTPException
from app.core.db_session import get_db
from sqlalchemy.orm import Session
from app.models.db_models import Trade
from app.schemas.pydantic_schemas import TradeResponse

trade_router = APIRouter(prefix="/trades", tags=["Trades"])

@trade_router.get("/get-trades/{account_name}", response_model=list[TradeResponse])
def get_trades_for_account(account_name: str, db: Session = Depends(get_db)):
    """Fetch all trades for a specific account using account_name."""
    print(f"CALLING {account_name}")
    trades = db.query(Trade).filter(Trade.account_name == account_name).all()
    if not trades:
        raise HTTPException(status_code=404, detail=f"No trades found for account '{account_name}'")
    return trades