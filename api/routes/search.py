from fastapi import APIRouter, Body, Depends
from typing import Dict, Any
from services.search_service import SearchService
from api.dependencies import get_search_service

router = APIRouter(prefix="/search", tags=["search"])


@router.post("")
async def search_documents(
    payload: Dict[str, Any] = Body(...),
    search_service: SearchService = Depends(get_search_service)
):
    """
    Search documents with pagination.
    
    Args:
        payload: Request payload containing query, page, and limit
        search_service: Search service instance (injected)
        
    Returns:
        Dictionary with results and pagination info
    """
    query = payload.get("query", "")
    page = payload.get("page", 1)
    limit = payload.get("limit", 50)
    
    return await search_service.search_documents(query, page, limit)

