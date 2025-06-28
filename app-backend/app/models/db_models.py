# db sqlalchemy model
# to create tables
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, ForeignKey, Boolean
from sqlalchemy.sql import func
from app.core.db_session import Base
from datetime import datetime, timezone

class Account(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    account_name = Column(String, unique=True, nullable=False)
    role = Column(String, nullable=False)
    api_key = Column(String, unique=True, nullable=False)
    api_secret = Column(String, nullable=False)
    risk_percentage = Column(Float, nullable=False)
    leverage = Column(Float, nullable=False)
    is_activate = Column(Boolean, default=True)
    is_deleted = Column(Boolean, default=False, server_default='false')
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # Auto-generated timestamp
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())  # Updated on every change

class Trade(Base):
    __tablename__ = "trades"
    id = Column(Integer, primary_key=True)
    order_id = Column(String, unique=True, index=True, nullable=False)
    account_name = Column(String, ForeignKey("accounts.account_name"), nullable=False)  # Foreign key to accounts
    symbol = Column(String, index=True)
    side = Column(String)
    order_type = Column(String)
    price = Column(Float)
    qty = Column(Float)
    status = Column(String)
    avg_price = Column(Float)
    cum_exec_qty = Column(Float)
    cum_exec_value = Column(Float)
    cum_exec_fee = Column(Float)
    closed_pnl = Column(Float)
    category = Column(String)
    created_time = Column(DateTime)
    updated_time = Column(DateTime)
    raw_event = Column(JSON)

class AlertLog(Base):
    __tablename__ = "alert_logs"

    id = Column(String, primary_key=True, index=True)
    data = Column(JSON, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    
class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(128), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    updated_at: Mapped[DateTime] = mapped_column(DateTime, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))