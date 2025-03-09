# app/database.py
from motor.motor_asyncio import AsyncIOMotorClient
from config import MONGO_URI, DATABASE_NAME

client = None
db = None

async def connect_to_mongo():
    global client, db
    try:
        client = AsyncIOMotorClient(MONGO_URI)
        db = client[DATABASE_NAME]
        print("✅ Connected to MongoDB")
    except Exception as e:
        print(f"❌ Error connecting to MongoDB: {e}")

async def close_mongo_connection():
    global client
    if client:
        client.close()
        print("❌ MongoDB connection closed")
