from sqlalchemy import create_engine, MetaData, Table, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get DATABASE_URL from environment
DATABASE_URL = os.environ.get("DATABASE_URL")

# Initialize SQLAlchemy components
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
metadata = MetaData()
Base = declarative_base()

# Reflect existing tables
trades_table = Table('trades', metadata, autoload_with=engine)
accounts_table = Table('accounts', metadata, autoload_with=engine)  # 👈 Add this line

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

# ✅ New: Fetch active accounts
def get_active_accounts():
    """
    Fetch all active accounts (where is_activate == True) from the accounts table.
    
    Returns:
        A dict in the format {account_name: {api_key: ..., api_secret: ...}, ...}
    """
    session = SessionLocal()
    try:
        query = select(accounts_table).where(accounts_table.c.is_activate == True)
        result = session.execute(query).mappings().fetchall()
        accounts_data = {
            row["account_name"]: {
                "api_key": row["api_key"],
                "api_secret": row["api_secret"],
            }
            for row in result
        }
        return accounts_data
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()
