from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from dotenv import load_dotenv
import os
# Load environment variables from .env file
load_dotenv()

# Get DATABASE_URL from environment
DATABASE_URL = os.environ.get("DATABASE_URL")

engine = create_engine(DATABASE_URL)

# Create a session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
metadata = MetaData()

trades_table = Table('trades', metadata, autoload_with=engine)

# Base class for models
Base = declarative_base()

# Example: Insert a trade
def insert_trade(trade_data):
    session = SessionLocal()
    try:
        session.execute(trades_table.insert().values(**trade_data))
        session.commit()
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()