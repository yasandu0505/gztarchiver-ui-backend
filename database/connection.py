from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from pymongo.database import Database
from config.settings import settings
import sys
from typing import List


def connect_to_db() -> MongoClient:
    """
    Connect to MongoDB using settings.
    
    Returns:
        MongoDB client instance
        
    Raises:
        SystemExit: If connection fails
    """
    mongodb_uri = settings.mongodb_uri
    
    if not mongodb_uri:
        print("❌ MONGODB_URI not found in environment")
        sys.exit(1)
    
    if mongodb_uri:
        print(f"✅ MONGODB_URI found: {mongodb_uri[:20]}...")
    
    try:
        client = MongoClient(mongodb_uri)
        client.admin.command('ping')
        print("✅ Connected to MongoDB successfully.")
        return client
    except ConnectionFailure as e:
        print("❌ Failed to connect to MongoDB:", e)
        sys.exit(1)


# Initialize database connection
client = connect_to_db()
db: Database = client.doc_db
collection_names: List[str] = db.list_collection_names()



