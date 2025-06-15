from pydantic import BaseModel, Field,EmailStr
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


class TradeResponse(BaseModel):
    id: int
    order_id: str
    account_name: str
    symbol: Optional[str]
    side: Optional[str]
    order_type: Optional[str]
    price: Optional[float]
    qty: Optional[float]
    status: Optional[str]
    avg_price: Optional[float]
    cum_exec_qty: Optional[float]
    cum_exec_value: Optional[float]
    cum_exec_fee: Optional[float]
    closed_pnl: Optional[float]
    category: Optional[str]
    created_time: Optional[datetime]
    updated_time: Optional[datetime]
    raw_event: Optional[dict]

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserSchema(UserBase):
    id: int

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email: str | None = None