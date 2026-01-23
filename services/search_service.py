import asyncio
from typing import Dict, Any, List, Tuple
from database.repository import DocumentRepository
from core.query_parser import QueryParser
from core.query_builder import QueryBuilder


class SearchService:
    """Service for document search operations"""
    
    def __init__(self, repository: DocumentRepository):
        """
        Initialize search service.
        
        Args:
            repository: Document repository instance
        """
        self.repository = repository
        self.query_parser = QueryParser()
        self.query_builder = QueryBuilder()
    
    async def search_documents(
        self,
        query: str,
        page: int = 1,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Search documents with pagination.
        
        Args:
            query: Search query string
            page: Page number (1-based)
            limit: Number of results per page
            
        Returns:
            Dictionary with results and pagination info
        """
        if not query:
            return self._empty_results(page, limit)
        
        # Parse the search query
        _, mongo_filters, free_text = self.query_parser.parse_search_query(query)
        
        # Build the MongoDB-style query (which repository matches in memory)
        search_query = self.query_builder.build_mongodb_query(mongo_filters, free_text)
        
        # Define projection
        projection = {
            "document_id": 1,
            "description": 1,
            "document_date": 1,
            "document_type": 1,
            "file_path": 1,
            "download_url": 1,
            "source": 1,
            "availability": 1
        }
        
        # Get count for pagination
        total_count = self.repository.count_documents(None, search_query)
        
        # Calculate offset
        offset = (page - 1) * limit
        
        all_matches = self.repository.find_documents(
            None, 
            search_query, 
            projection, 
            skip=0, 
            limit=1000000 # Large number to get all for sorting
        )
        
        # Sort by date (newest first)
        sorted_results = sorted(
            all_matches,
            key=lambda x: x.get("document_date", ""),
            reverse=True
        )
        
        # Apply pagination
        paginated_results = sorted_results[offset : offset + limit]
        
        # Calculate pagination info
        total_pages = (total_count + limit - 1) // limit if total_count > 0 else 0
        has_next = page < total_pages
        has_prev = page > 1
        
        return {
            "results": paginated_results,
            "pagination": {
                "current_page": page,
                "total_pages": total_pages,
                "total_count": total_count,
                "limit": limit,
                "has_next": has_next,
                "has_prev": has_prev,
                "start_index": offset + 1 if total_count > 0 else 0,
                "end_index": min(offset + len(paginated_results), total_count)
            },
            "query_info": {
                "parsed_query": query,
                "target_collections": "global_metadata",
                "filters_applied": len(mongo_filters),
                "has_free_text": bool(free_text),
                "search_query": str(search_query) 
            }
        }
    
    def _empty_results(self, page: int, limit: int) -> Dict[str, Any]:
        """Return empty results structure."""
        return {
            "results": [],
            "pagination": {
                "current_page": page,
                "total_pages": 0,
                "total_count": 0,
                "limit": limit,
                "has_next": False,
                "has_prev": False
            }
        }
