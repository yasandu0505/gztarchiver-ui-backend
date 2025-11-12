import asyncio
from typing import Dict, Any, List, Tuple
from database.repository import DocumentRepository
from database.connection import collection_names
from core.query_parser import QueryParser
from core.query_builder import QueryBuilder


class SearchService:
    """Service for document search operations with parallel processing"""
    
    def __init__(self, repository: DocumentRepository):
        """
        Initialize search service.
        
        Args:
            repository: Document repository instance
        """
        self.repository = repository
        self.query_parser = QueryParser()
        self.query_builder = QueryBuilder()
        # Cache existing collections to avoid repeated checks
        self._existing_collections_cache = None
    
    def _get_existing_collections(self, collections: List[str]) -> List[str]:
        """
        Get list of existing collections (cached).
        
        Args:
            collections: List of collection names to check
            
        Returns:
            List of existing collection names
        """
        if self._existing_collections_cache is None:
            all_collections = set(self.repository.db.list_collection_names())
            self._existing_collections_cache = [
                col for col in collections if col in all_collections
            ]
        return self._existing_collections_cache
    
    async def search_documents(
        self,
        query: str,
        page: int = 1,
        limit: int = 50
    ) -> Dict[str, Any]:
        """
        Search documents with pagination using parallel processing.
        
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
        target_collections, mongo_filters, free_text = self.query_parser.parse_search_query(query)
        
        # Determine which collections to search
        if target_collections:
            collections_to_search = target_collections
        else:
            collections_to_search = self.repository.get_all_collection_names()
        
        # Reset cache when collections change
        self._existing_collections_cache = None
        
        # Get existing collections once (cached)
        existing_collections = self._get_existing_collections(collections_to_search)
        
        if not existing_collections:
            return self._empty_results(page, limit)
        
        # Build the MongoDB query
        search_query = self.query_builder.build_mongodb_query(mongo_filters, free_text)
        
        # Calculate offset
        offset = (page - 1) * limit
        
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
        
        # Get total count and all results in parallel
        total_count, all_results = await self._search_collections_parallel(
            existing_collections,
            search_query,
            projection
        )
        
        # Sort the collected results by date (newest first)
        sorted_results = sorted(
            all_results,
            key=lambda x: x.get("document_date", ""),
            reverse=True
        )
        
        # Apply pagination after sorting
        paginated_results = sorted_results[offset:offset + limit]
        
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
                "target_collections": target_collections if target_collections else "all",
                "filters_applied": len(mongo_filters),
                "has_free_text": bool(free_text),
                "search_query": str(search_query)  # Debug info
            }
        }
    
    async def _search_collections_parallel(
        self,
        collections: List[str],
        query: Dict[str, Any],
        projection: Dict[str, Any]
    ) -> Tuple[int, List[Dict[str, Any]]]:
        """
        Search all collections in parallel and return count and results.
        
        Args:
            collections: List of collection names to search
            query: MongoDB query dictionary
            projection: Fields to include in results
            
        Returns:
            Tuple of (total_count, all_results)
        """
        # Get event loop
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.get_event_loop()
        
        # Create tasks for parallel execution
        count_tasks = [
            loop.run_in_executor(
                None,
                self.repository.count_documents,
                col_name,
                query
            )
            for col_name in collections
        ]
        
        # Limit results per collection to avoid memory issues
        # For pagination, we need enough results to sort properly
        # Using a reasonable limit per collection (can be adjusted based on needs)
        max_results_per_collection = 1000
        
        search_tasks = [
            loop.run_in_executor(
                None,
                self.repository.find_documents,
                col_name,
                query,
                projection,
                0,  # No skip - we'll get all results
                max_results_per_collection  # Limit per collection
            )
            for col_name in collections
        ]
        
        # Execute all tasks in parallel
        count_results, search_results = await asyncio.gather(
            asyncio.gather(*count_tasks, return_exceptions=True),
            asyncio.gather(*search_tasks, return_exceptions=True)
        )
        
        # Aggregate counts
        total_count = 0
        for count_result in count_results:
            if isinstance(count_result, int):
                total_count += count_result
            elif isinstance(count_result, Exception):
                print(f"Error counting documents: {count_result}")
        
        # Aggregate search results
        all_results = []
        for search_result in search_results:
            if isinstance(search_result, list):
                all_results.extend(search_result)
            elif isinstance(search_result, Exception):
                print(f"Error searching documents: {search_result}")
        
        return total_count, all_results
    
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

