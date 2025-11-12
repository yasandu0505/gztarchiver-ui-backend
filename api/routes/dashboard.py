from fastapi import APIRouter, Depends
from services.dashboard_service import DashboardService
from api.dependencies import get_dashboard_service

router = APIRouter(prefix="/dashboard-status", tags=["dashboard"])


@router.get("")
async def get_dashboard_status(
    dashboard_service: DashboardService = Depends(get_dashboard_service)
):
    """
    Get dashboard status with caching and parallel processing.
    
    Args:
        dashboard_service: Dashboard service instance (injected)
        
    Returns:
        Dictionary with dashboard statistics
    """
    return await dashboard_service.get_dashboard_status()

