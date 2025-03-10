# db sqlalchemy model
# to create tables

from sqlalchemy import Column, String, Boolean, Integer, Float, DateTime
from sqlalchemy.sql import func
from core.db_session import Base

class User(Base):
    __tablename__ = "accounts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    account_name = Column(String, unique=True, nullable=False)
    role = Column(String, nullable=False)
    api_key = Column(String, unique=True, nullable=False)
    api_secret = Column(String, nullable=False)
    risk_percentage = Column(Float, nullable=False)
    leverage = Column(Float, nullable=False)
    is_activate = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # Auto-generated timestamp
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())  # Updated on every change
