from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class AccountBase(BaseModel):
    account_name: str
    role: str
    api_key: str
    api_secret: str
    risk_percentage: float
    leverage: float
    is_activate: Optional[bool] = True

class AccountCreate(BaseModel):
    account_name: str
    role: str
    api_key: str
    api_secret: str
    risk_percentage: float
    leverage: float
    is_activate: Optional[bool] = True
    
class AccountUpdate(BaseModel):
    account_name: Optional[str] = None
    role: Optional[str] = None
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    risk_percentage: Optional[float] = None
    leverage: Optional[float] = None
    is_activate: Optional[bool] = True

class AccountResponse(BaseModel):
    id: int
    account_name: str
    role: str
    api_key: str
    api_secret: str
    risk_percentage: float
    leverage: float
    is_activate: Optional[bool] = True
    created_at: datetime
    last_updated: datetime | None = Field(default=None) 

    class Config:
        from_attributes = True  # To allow ORM conversion
        
# schema for alert from tradingview
class TradingViewAlert(BaseModel):
    account: str
    action: str
    symbol: str
    side: str = None  # Only for close/trailing stop loss
    leverage: int = None
    entry_price: float = None
    stop_loss: float = None
    stop_loss_percentage: float = None
    tps: list[float] = []
    tp_sizes: list[float] = []
    risk_percentage: float = None
    commission_percentage: float = None
    margin_type: str = None