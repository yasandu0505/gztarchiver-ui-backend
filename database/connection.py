from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import load_dotenv
import os
import sys

def connec_to_db():
    load_dotenv()
    MONGODB_URI = os.getenv("MONGODB_URI")
    try:
        client = MongoClient(MONGODB_URI)
        client.admin.command('ping')
        print("✅ Connected to MongoDB successfully.")
        return client
    except ConnectionFailure as e:
        print("❌ Failed to connect to MongoDB:", e)
        sys.exit(1)
        return None

client = connec_to_db()
db = client.doc_db
collection_names = db.list_collection_names()



