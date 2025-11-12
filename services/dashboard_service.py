import asyncio
from typing import Dict, Any, List
from functools import lru_cache
from database.repository import DocumentRepository
from database.connection import collection_names
from services.cache_service import CacheService
from config.settings import settings


class DashboardService:
    """Service for dashboard statistics and caching"""
    
    def __init__(self, repository: DocumentRepository, cache_service: CacheService):
        """
        Initialize dashboard service.
        
        Args:
            repository: Document repository instance
            cache_service: Cache service instance
        """
        self.repository = repository
        self.cache_service = cache_service
        self.cache_key = "dashboard_data"
    
    @lru_cache(maxsize=1)
    def get_years_covered(self) -> Dict[str, int]:
        """
        Get years covered by gazette collections (cached).
        
        Returns:
            Dictionary with 'from' and 'to' years
        """
        years = sorted([
            int(col.replace("gazettes_", ""))
            for col in collection_names
            if col.startswith("gazettes_") and col.replace("gazettes_", "").isdigit()
        ])
        return {"from": years[0], "to": years[-1]} if years else {}
    
    async def get_collection_stats_async(self, collection_name: str) -> Dict[str, Any]:
        """
        Get statistics for a single collection asynchronously.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Dictionary with total_docs, available_docs, and document_types
        """
        # Run in thread pool since repository methods are synchronous
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.repository.get_collection_stats,
            collection_name
        )
    
    async def get_dashboard_status(self) -> Dict[str, Any]:
        """
        Get dashboard status with caching and parallel processing.
        
        Returns:
            Dictionary with dashboard statistics
        """
        # Check cache first
        cached_data = self.cache_service.get(self.cache_key)
        if cached_data is not None:
            return cached_data
        
        # Get years covered (cached)
        years_covered = self.get_years_covered()
        
        # Get all collection names
        collection_names_list = self.repository.get_all_collection_names()
        
        # Process all collections in parallel
        tasks = [
            self.get_collection_stats_async(col)
            for col in collection_names_list
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Aggregate results
        total_docs = 0
        available_docs = 0
        all_document_types = set()
        
        for result in results:
            if isinstance(result, dict):
                total_docs += result.get("total_docs", 0)
                available_docs += result.get("available_docs", 0)
                all_document_types.update(result.get("document_types", []))
        
        # Clean and format document types
        document_types = sorted([
            doc_type.title().strip().replace("_", " ")
            for doc_type in all_document_types
            if doc_type
        ])
        
        response_data = {
            "total_docs": total_docs,
            "available_docs": available_docs,
            "document_types": document_types,
            "years_covered": years_covered
        }
        
        # Cache the result
        self.cache_service.set(self.cache_key, response_data)
        
        return response_data

