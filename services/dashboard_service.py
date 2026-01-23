import asyncio
from typing import Dict, Any, List
from functools import lru_cache
from database.repository import DocumentRepository
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
    
    def get_years_covered(self) -> Dict[str, int]:
        """
        Get years covered by gazette collections (dynamically calculated)
        """
        try:
            docs = self.repository.store.get_all_documents()
            if not docs:
                return {}
            
            years = set()
            for doc in docs:
                date_str = doc.get("document_date", "")
                if date_str and len(date_str) >= 4 and date_str[:4].isdigit():
                    years.add(int(date_str[:4]))
            
            if not years:
                return {}
                
            sorted_years = sorted(list(years))
            return {"from": sorted_years[0], "to": sorted_years[-1]}
        except Exception:
            return {}

    
    async def get_dashboard_status(self) -> Dict[str, Any]:
        """
        Get dashboard status with caching.
        
        Returns:
            Dictionary with dashboard statistics
        """
        # Check cache first
        cached_data = self.cache_service.get(self.cache_key)
        if cached_data is not None:
            return cached_data
        
        # In the new single-source-of-truth model, repository.get_collection_stats calculates everything
        stats = self.repository.get_collection_stats()
        
        # Get years covered
        years_covered = self.get_years_covered()
        
        # Clean and format document types
        document_types = sorted([
            doc_type.title().strip().replace("_", " ")
            for doc_type in stats.get("document_types", [])
            if doc_type
        ])
        
        response_data = {
            "total_docs": stats.get("total_docs", 0),
            "available_docs": stats.get("available_docs", 0),
            "document_types": document_types,
            "years_covered": years_covered
        }
        
        # Cache the result
        self.cache_service.set(self.cache_key, response_data)
        
        return response_data
