from typing import Dict, Any, List, Optional
from services.metadata_store import MetadataStore
import re
import logging
import pandas as pd

class DocumentRepository:
    """Repository for document operations using global metadata store"""
    
    def __init__(self):
        """
        Initialize document repository.
        """
        self.store = MetadataStore()
    
    def get_dashboard_stats(self) -> Dict[str, Any]:
        """
        Get statistics for documents.
            
        Returns:
            Dictionary with total_docs, available_docs, and document_types
        """
        try:
            document_data_frame = pd.DataFrame(self.store.get_all_documents())
            
            total_docs = len(document_data_frame)
            available_docs = len(document_data_frame[document_data_frame["availability"] == "Available"])
            document_types = (document_data_frame["document_type"].dropna().unique().tolist())
            
            return {
                "total_docs": total_docs,
                "available_docs": available_docs,
                "document_types": document_types
            }
        except Exception as e:
            logging.error(f"Error getting stats: {e}")
            return {"total_docs": 0, "available_docs": 0, "document_types": []}
    
    def count_documents(self, query: Dict[str, Any]) -> int:
        """
        Count documents matching a query.
        
        Args:
            query: Query dictionary
            
        Returns:
            Number of matching documents
        """
        try:
            document_data_frame = pd.DataFrame(self.store.get_all_documents())
            count = document_data_frame.apply(
                lambda row: self._match_document(row.to_dict(), query),
                axis=1
            ).sum()
            return int(count)
        except Exception as e:
            logging.error(f"Error counting documents: {e}")
            return 0

    def find_documents(
        self,
        query: Dict[str, Any],
        projection: Optional[Dict[str, Any]] = None,
        skip: int = 0,
        limit: int = 50,
        sort_key: Optional[str] = None,
        reverse: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Find documents matching a query.
        
        Args:
            query: Query dictionary
            projection: Fields to include (simple inclusion only for now)
            skip: Number to skip
            limit: Max to return
            
        Returns:
            List of documents
        """
        try:
            document_data_frame = pd.DataFrame(self.store.get_all_documents())
            
            filtered_docs = document_data_frame[document_data_frame.apply(
                lambda row: self._match_document(row.to_dict(), query),
                axis=1
            )]

            # sorting
            # sorting
            if sort_key:
                sorted_data_frame = filtered_docs.sort_values(by=sort_key, ascending=not reverse)
            else:
                sorted_data_frame = filtered_docs
                
            # pagination
            paginated_docs = sorted_data_frame[skip : skip + limit]

            # Filter fields based on the projection dictionary.
            # If a projection is provided, only fields with value 1 are included in the result.
            if projection:
                fields = [k for k, v in projection.items() if v == 1]
                paginated_docs = paginated_docs[fields]

            return paginated_docs.to_dict(orient="records")

        except Exception as e:
            logging.error(f"Error finding documents: {e}")
            return []

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
                            if doc_val is None or doc_val <= val:
                                return False
                        elif op == "$gte":
                            if doc_val is None or doc_val < val:
                                return False
                        elif op == "$lt":
                            if doc_val is None or doc_val >= val:
                                return False
                        elif op == "$lte":
                            if doc_val is None or doc_val > val:
                                return False
                else:
                    # Direct equality
                    if doc_val != condition:
                        return False
                        
        return True
