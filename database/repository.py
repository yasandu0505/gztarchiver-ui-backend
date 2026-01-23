from typing import Dict, Any, List, Optional
from services.metadata_store import MetadataStore
import re

class DocumentRepository:
    """Repository for document operations using global metadata store"""
    
    def __init__(self):
        """
        Initialize document repository.
        """
        self.store = MetadataStore()
    
    def get_collection_stats(self, collection_name: str = None) -> Dict[str, Any]:
        """
        Get statistics for documents.
        
        Args:
            collection_name: Ignored, kept for compatibility.
            
        Returns:
            Dictionary with total_docs, available_docs, and document_types
        """
        try:
            documents = self.store.get_all_documents()
            
            total_docs = len(documents)
            available_docs = sum(1 for doc in documents if doc.get("availability") == "Available")
            document_types = list(set(doc.get("document_type") for doc in documents if doc.get("document_type")))
            
            return {
                "total_docs": total_docs,
                "available_docs": available_docs,
                "document_types": document_types
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {"total_docs": 0, "available_docs": 0, "document_types": []}
    
    def count_documents(self, collection_name: str, query: Dict[str, Any]) -> int:
        """
        Count documents matching a query.
        
        Args:
            collection_name: Ignored
            query: Query dictionary
            
        Returns:
            Number of matching documents
        """
        try:
            documents = self.store.get_all_documents()
            return sum(1 for doc in documents if self._match_document(doc, query))
        except Exception as e:
            print(f"Error counting documents: {e}")
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
        Find documents matching a query.
        
        Args:
            collection_name: Ignored
            query: Query dictionary
            projection: Fields to include (simple inclusion only for now)
            skip: Number to skip
            limit: Max to return
            
        Returns:
            List of documents
        """
        try:
            documents = self.store.get_all_documents()
            filtered_docs = [doc for doc in documents if self._match_document(doc, query)]
            
            # Apply sorting implicitly 
            # Apply pagination
            paginated_docs = filtered_docs[skip : skip + limit]
            
            # Apply projection (simple version)
            if projection:
                projected_docs = []
                for doc in paginated_docs:
                    new_doc = {}
                    for key, val in projection.items():
                        if val == 1 and key in doc:
                            new_doc[key] = doc[key]
                    projected_docs.append(new_doc)
                return projected_docs
            
            return paginated_docs
        except Exception as e:
            print(f"Error finding documents: {e}")
            return []
    
    def get_all_collection_names(self) -> List[str]:
        """
        Get mock collection names.
        
        Returns:
            List containing a single dummy collection name.
        """
        return ["global_metadata"]
    
    def collection_exists(self, collection_name: str) -> bool:
        """Check if collection exists."""
        return True

    def _match_document(self, doc: Dict[str, Any], query: Dict[str, Any]) -> bool:
        """
        Match a document against a MongoDB-style query.
        Supports: equality, $regex, $gt, $gte, $lt, $lte, $ne, $and, $or
        """
        if not query:
            return True
            
        for key, condition in query.items():
            if key == "$and":
                if not all(self._match_document(doc, subq) for subq in condition):
                    return False
            elif key == "$or":
                if not any(self._match_document(doc, subq) for subq in condition):
                    return False
            else:
                # Field match
                doc_val = doc.get(key)
                if isinstance(condition, dict):
                    # Operator match
                    for op, val in condition.items():
                        if op == "$regex":
                            flags = 0
                            if condition.get("$options") == "i":
                                flags = re.IGNORECASE
                            if not re.search(val, str(doc_val or ""), flags):
                                return False
                        elif op == "$eq":
                            if doc_val != val:
                                return False
                        elif op == "$ne":
                            if doc_val == val:
                                return False
                        elif op == "$gt":
                            if not (doc_val and doc_val > val):
                                return False
                        elif op == "$gte":
                            if not (doc_val and doc_val >= val):
                                return False
                        elif op == "$lt":
                            if not (doc_val and doc_val < val):
                                return False
                        elif op == "$lte":
                            if not (doc_val and doc_val <= val):
                                return False
                else:
                    # Direct equality
                    if doc_val != condition:
                        return False
                        
        return True
