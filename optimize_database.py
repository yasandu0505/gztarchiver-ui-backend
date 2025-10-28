#!/usr/bin/env python3
"""
Database optimization script for GZT Archiver
Creates indexes to improve dashboard-status endpoint performance
"""

from database import db, collection_names
import time

def create_indexes():
    """Create optimized indexes for dashboard queries"""
    print("Creating database indexes for optimization...")
    
    indexes_created = 0
    
    for collection_name in collection_names:
        try:
            collection = db[collection_name]
            
            # Index for availability field (most important for dashboard)
            collection.create_index("availability")
            print(f"✓ Created availability index on {collection_name}")
            
            # Compound index for availability + document_type
            collection.create_index([("availability", 1), ("document_type", 1)])
            print(f"✓ Created compound index (availability, document_type) on {collection_name}")
            
            # Index for document_type for faster aggregation
            collection.create_index("document_type")
            print(f"✓ Created document_type index on {collection_name}")
            
            # Index for document_date for year-based queries
            collection.create_index("document_date")
            print(f"✓ Created document_date index on {collection_name}")
            
            indexes_created += 4
            
        except Exception as e:
            print(f"✗ Error creating indexes for {collection_name}: {e}")
    
    print(f"\n🎉 Successfully created {indexes_created} indexes across {len(collection_names)} collections")
    return indexes_created

def analyze_collection_stats():
    """Analyze collection statistics for optimization insights"""
    print("\nAnalyzing collection statistics...")
    
    for collection_name in collection_names:
        try:
            collection = db[collection_name]
            
            # Get collection stats
            total_docs = collection.count_documents({})
            available_docs = collection.count_documents({"availability": "Available"})
            
            # Get unique document types count
            doc_types = collection.distinct("document_type")
            
            print(f"\n📊 {collection_name}:")
            print(f"   Total documents: {total_docs:,}")
            print(f"   Available documents: {available_docs:,} ({available_docs/total_docs*100:.1f}%)")
            print(f"   Unique document types: {len(doc_types)}")
            
        except Exception as e:
            print(f"✗ Error analyzing {collection_name}: {e}")

def test_query_performance():
    """Test query performance before and after optimization"""
    print("\nTesting query performance...")
    
    test_collection = collection_names[0] if collection_names else None
    if not test_collection:
        print("No collections found for testing")
        return
    
    collection = db[test_collection]
    
    # Test 1: Count all documents
    start_time = time.time()
    total_count = collection.count_documents({})
    count_time = time.time() - start_time
    print(f"📈 Count all documents: {count_time:.3f}s ({total_count:,} docs)")
    
    # Test 2: Count available documents
    start_time = time.time()
    available_count = collection.count_documents({"availability": "Available"})
    available_time = time.time() - start_time
    print(f"📈 Count available documents: {available_time:.3f}s ({available_count:,} docs)")
    
    # Test 3: Aggregate pipeline (new optimized method)
    start_time = time.time()
    pipeline = [
        {
            "$group": {
                "_id": None,
                "total_docs": {"$sum": 1},
                "available_docs": {
                    "$sum": {
                        "$cond": [
                            {"$eq": ["$availability", "Available"]},
                            1,
                            0
                        ]
                    }
                },
                "document_types": {"$addToSet": "$document_type"}
            }
        }
    ]
    result = list(collection.aggregate(pipeline))
    agg_time = time.time() - start_time
    print(f"📈 Aggregation pipeline: {agg_time:.3f}s")

if __name__ == "__main__":
    print("🚀 GZT Archiver Database Optimization")
    print("=" * 50)
    
    # Analyze current state
    analyze_collection_stats()
    
    # Create indexes
    indexes_created = create_indexes()
    
    # Test performance
    test_query_performance()
    
    print("\n✅ Database optimization complete!")
    print("\n💡 Performance Tips:")
    print("   - Dashboard data is now cached for 5 minutes")
    print("   - Queries run in parallel across collections")
    print("   - Aggregation pipelines are more efficient than multiple queries")
    print("   - Indexes will speed up availability and document_type queries")
