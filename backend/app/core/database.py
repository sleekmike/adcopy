"""
Database configuration and initialization
"""
from pymongo import MongoClient
from app.core.config import settings

class Database:
    client: MongoClient = None
    database = None

db = Database()

async def init_database():
    """Initialize database connection"""
    try:
        # Create PyMongo client (sync)
        db.client = MongoClient(settings.MONGODB_URL)
        db.database = db.client[settings.DATABASE_NAME]
        
        # Test connection
        db.client.admin.command('ping')
        print(f"✅ Connected to MongoDB: {settings.DATABASE_NAME}")
        
    except Exception as e:
        print(f"⚠️ MongoDB connection failed: {e}")
        print("🔄 App will run without database persistence")
        db.client = None
        db.database = None

async def close_database():
    """Close database connection"""
    if db.client:
        db.client.close()
        print("Disconnected from MongoDB")
