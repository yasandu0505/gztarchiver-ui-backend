from typing import Dict, Any, List, Optional
from pymongo.collection import Collection
from pymongo.database import Database
from database.connection import db, collection_names
from database.schema import serialize_doc


class DocumentRepository:
    """Repository for document database operations"""
    
    def __init__(self, database: Optional[Database] = None):
        """
        Initialize document repository.
        
        Args:
            database: MongoDB database instance. If not provided, uses global db.
        """
        self.db = database or db
        self.collection_names = collection_names
    
    def get_collection_stats(self, collection_name: str) -> Dict[str, Any]:
        """
        Get statistics for a single collection using aggregation pipeline.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Dictionary with total_docs, available_docs, and document_types
        """
        try:
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
            
            result = list(self.db[collection_name].aggregate(pipeline))
            if result:
                return {
                    "total_docs": result[0]["total_docs"],
                    "available_docs": result[0]["available_docs"],
                    "document_types": [dt for dt in result[0]["document_types"] if dt]
                }
            else:
                return {"total_docs": 0, "available_docs": 0, "document_types": []}
        except Exception as e:
            print(f"Error processing collection {collection_name}: {e}")
            return {"total_docs": 0, "available_docs": 0, "document_types": []}
    
    def count_documents(self, collection_name: str, query: Dict[str, Any]) -> int:
        """
        Count documents in a collection matching a query.
        
        Args:
            collection_name: Name of the collection
            query: MongoDB query dictionary
            
        Returns:
            Number of matching documents
        """
        try:
            if collection_name not in self.db.list_collection_names():
                return 0
            return self.db[collection_name].count_documents(query)
        except Exception as e:
            print(f"Error counting documents in {collection_name}: {e}")
            return 0
    
    def find_documents(
        self,
        collection_name: str,
        query: Dict[str, Any],
        projection: Optional[Dict[str, Any]] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Find documents in a collection matching a query.
        
        Args:
            collection_name: Name of the collection
            query: MongoDB query dictionary
            projection: Fields to include in results
            skip: Number of documents to skip
            limit: Maximum number of documents to return
            
        Returns:
            List of serialized documents
        """
        try:
            if collection_name not in self.db.list_collection_names():
                return []
            
            collection: Collection = self.db[collection_name]
            cursor = collection.find(query, projection).skip(skip).limit(limit)
            return [serialize_doc(doc) for doc in cursor]
        except Exception as e:
            print(f"Error searching collection {collection_name}: {e}")
            return []
    
    def get_all_collection_names(self) -> List[str]:
        """
        Get all collection names.
        
        Returns:
            List of collection names
        """
        return self.collection_names
    
    def collection_exists(self, collection_name: str) -> bool:
        """
        Check if a collection exists.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            True if collection exists, False otherwise
        """
        return collection_name in self.db.list_collection_names()

