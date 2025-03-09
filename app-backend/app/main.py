# app/main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from core.db_session import connect_to_mongo, close_mongo_connection
from api.v1 import endpoints

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()  # Connect to MongoDB
    yield  # The application runs while this is active
    await close_mongo_connection()  # Disconnect MongoDB when shutting down

app = FastAPI(lifespan=lifespan)

app.include_router(endpoints.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "FastAPI with MongoDB is running 🚀"}
