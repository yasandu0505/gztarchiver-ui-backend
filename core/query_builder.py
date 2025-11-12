from typing import Dict, Any


class QueryBuilder:
    """Builder for MongoDB queries combining filters and free text search"""
    
    @staticmethod
    def build_mongodb_query(mongo_filters: Dict[str, Any], free_text: str) -> Dict[str, Any]:
        """
        Build the final MongoDB query combining filters and free text search.
        
        Args:
            mongo_filters: Dictionary of MongoDB filter conditions
            free_text: Free text search string
            
        Returns:
            MongoDB query dictionary
        """
        query_parts = []
        
        # Add structured filters
        for field, filter_condition in mongo_filters.items():
            query_parts.append({field: filter_condition})
        
        # Add free text search if present
        if free_text:
            text_search = {
                "$or": [
                    {"document_type": {"$regex": free_text, "$options": "i"}},
                    {"description": {"$regex": free_text, "$options": "i"}},
                    {"document_id": {"$regex": free_text, "$options": "i"}},
                    {"document_date": free_text}  # Exact match for full dates
                ]
            }
            
            # If free text looks like a date pattern, add partial date matching
            if free_text.replace("-", "").isdigit() and len(free_text) >= 4:
                text_search["$or"].append({
                    "document_date": {"$regex": f"^{free_text}", "$options": "i"}
                })
            
            query_parts.append(text_search)
        
        # Combine all parts with AND logic
        if len(query_parts) == 0:
            return {}  # Empty query means get all documents
        elif len(query_parts) == 1:
            return query_parts[0]
        else:
            return {"$and": query_parts}

