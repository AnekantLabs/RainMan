# from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, create_engine,ForeignKey
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# from datetime import datetime
# Base = declarative_base()
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os

load_dotenv()  # Load variables from .env
DATABASE_URL = os.getenv("DATABASE_URL")
# class Trade(Base):
#     __tablename__ = "trades"
#     id = Column(Integer, primary_key=True)
#     order_id = Column(String, unique=True, index=True, nullable=False)
#     symbol = Column(String, index=True)
#     side = Column(String)
#     order_type = Column(String)
#     price = Column(Float)
#     qty = Column(Float)
#     status = Column(String)
#     avg_price = Column(Float)
#     cum_exec_qty = Column(Float)
#     cum_exec_value = Column(Float)
#     cum_exec_fee = Column(Float)
#     closed_pnl = Column(Float)
#     category = Column(String)
#     created_time = Column(DateTime)
#     updated_time = Column(DateTime)
#     raw_event = Column(JSON)
#     account_name = Column(String, ForeignKey("accounts.account_name"), nullable=False)  # Foreign key to accounts

# DB setup (adjust URI as needed)
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)



