# app/main.py
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.core.db_session import engine, Base, get_db
from app.models import db_models
# Import your routers here
from app.api.v1 import accounts

app = FastAPI()

# Create tables in the database
Base.metadata.create_all(bind=engine)

app.include_router(accounts.acc_router, prefix="/api/v1")

@app.on_event("startup")
async def startup_db():
    """Ensures that the database is connected when the server starts"""
    try:
        with engine.connect() as connection:
            print("✅ Successfully connected to the PostgreSQL database!")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

# Example route to test database connection
@app.get("/")
def read_root(db: Session = Depends(get_db)):
    return {"message": "PostgreSQL is connected!"}
