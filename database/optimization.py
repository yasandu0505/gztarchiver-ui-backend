from typing import List
from database.connection import db, collection_names


def optimize_database_indexes() -> None:
    """
    Automatically create indexes on startup for better performance.
    Creates indexes on availability, document_type, and compound indexes.
    """
    try:
        print("🔧 Optimizing database indexes...")
        for collection_name in collection_names:
            try:
                collection = db[collection_name]
                # Create essential indexes
                collection.create_index("availability")
                collection.create_index([("availability", 1), ("document_type", 1)])
                collection.create_index("document_type")
                print(f"✓ Optimized {collection_name}")
            except Exception as e:
                print(f"⚠️  Could not optimize {collection_name}: {e}")
        print("✅ Database optimization complete!")
    except Exception as e:
        print(f"⚠️  Database optimization failed: {e}")

