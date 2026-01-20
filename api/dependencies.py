# from functools import lru_cache
# from database.repository import DocumentRepository
# from clients.query_api_client import QueryAPIClient
# from services.cache_service import CacheService
# from services.dashboard_service import DashboardService
# from services.search_service import SearchService
# from services.document_service import DocumentService


# @lru_cache()
# def get_document_repository() -> DocumentRepository:
#     """Get document repository instance (singleton)."""
#     return DocumentRepository()


# @lru_cache()
# def get_query_api_client() -> QueryAPIClient:
#     """Get query API client instance (singleton)."""
#     return QueryAPIClient()


# @lru_cache()
# def get_cache_service() -> CacheService:
#     """Get cache service instance (singleton)."""
#     return CacheService()


# @lru_cache()
# def get_dashboard_service() -> DashboardService:
#     """Get dashboard service instance (singleton)."""
#     repository = get_document_repository()
#     cache_service = get_cache_service()
#     return DashboardService(repository, cache_service)


# @lru_cache()
# def get_search_service() -> SearchService:
#     """Get search service instance (singleton)."""
#     repository = get_document_repository()
#     return SearchService(repository)


# @lru_cache()
# def get_document_service() -> DocumentService:
#     """Get document service instance (singleton)."""
#     api_client = get_query_api_client()
#     return DocumentService(api_client)

