# app/main.py
import asyncio
from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from app.core.db_session import engine, Base, get_db, setup_trade_notify_trigger
from app.models import db_models
# Import your routers here
from app.api.v1 import accounts, alerts,trades,users,auth
from fastapi.middleware.cors import CORSMiddleware
from app.websockets.trades_ws import listen_to_db

app = FastAPI()

# allow to access frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # React frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables in the database
Base.metadata.create_all(bind=engine)

app.include_router(accounts.acc_router, prefix="/v1")
app.include_router(trades.trade_router, prefix="/v1")
app.include_router(alerts.alert_router, prefix="/v1")
app.include_router(users.user_router, prefix="/v1")
app.include_router(auth.auth_router, prefix="/v1")


@app.on_event("startup")
async def startup_db():
    """Ensures that the database is connected when the server starts"""
    try:
        with engine.connect() as connection:
            print("✅ Successfully connected to the PostgreSQL database!")
        asyncio.create_task(listen_to_db())
        setup_trade_notify_trigger()  # <-- Call it here
        print("✅ Trigger setup (if not already existing)")
    except Exception as e:
        print(f"❌ Database connection failed: {e}")

# Example route to test database connection
@app.get("/")
def read_root(db: Session = Depends(get_db)):
    return {"message": "PostgreSQL is connected!"}

@app.on_event("shutdown")
def clear_logs_on_shutdown():
    print("🔴 Clearing worker_logs from Redis...")
    r.delete("worker_logs")