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

class AccountResponse(BaseModel):
    id: int
    account_name: str
    role: str
    risk_percentage: float
    leverage: int
    is_activate: Optional[bool] = True
    created_at: datetime
    last_updated: datetime | None = Field(default=None) 

    class Config:
        from_attributes = True  # To allow ORM conversion