from fastapi import APIRouter, Depends
from sqlmodel import Session

from backend.app.core.database import get_session
from backend.app.schemas.analytics import AnalyticsStats
from backend.app.modules.analytics.analytics_service import AnalyticsService

router = APIRouter()


@router.get("", response_model=AnalyticsStats, summary="Get productivity analytics stats")
@router.get("/stats", response_model=AnalyticsStats, summary="Get productivity analytics stats")
def get_analytics(
    session: Session = Depends(get_session),
):
    """Retrieve overview productivity metrics, completion rate, overdue counts, and breakdowns."""
    return AnalyticsService.get_stats(session=session)
