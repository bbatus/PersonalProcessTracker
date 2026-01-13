"""
Analytics API endpoints with authorization
"""

from datetime import date, datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.services.analytics_service import AnalyticsService

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


# Pydantic schemas
class DailyAnalyticsResponse(BaseModel):
    date: str
    total_tasks: int
    completed_tasks: int
    skipped_tasks: int
    pending_tasks: int
    completion_rate: float


class WeeklyAnalyticsResponse(BaseModel):
    start_date: str
    end_date: str
    total_tasks: int
    completed_tasks: int
    skipped_tasks: int
    pending_tasks: int
    completion_rate: float
    daily_breakdown: List[DailyAnalyticsResponse]


class CategoryStats(BaseModel):
    category_id: str
    category_name: str
    total: int
    completed: int
    skipped: int
    pending: int
    completion_rate: float


class MonthlyAnalyticsResponse(BaseModel):
    year: int
    month: int
    total_tasks: int
    completed_tasks: int
    skipped_tasks: int
    pending_tasks: int
    completion_rate: float
    category_breakdown: List[CategoryStats]


class TaskInsight(BaseModel):
    title: str
    count: int


class TaskInsightsResponse(BaseModel):
    most_completed: List[TaskInsight]
    most_skipped: List[TaskInsight]


class HeatmapData(BaseModel):
    date: str
    total_tasks: int
    completed_tasks: int
    completion_rate: float


@router.get("/daily", response_model=DailyAnalyticsResponse)
def get_daily_analytics(
    target_date: date = Query(..., description="Date to analyze"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get daily analytics for the authenticated user"""
    service = AnalyticsService(db)
    
    analytics = service.get_daily_analytics(current_user.id, target_date)
    
    return DailyAnalyticsResponse(**analytics)


@router.get("/weekly", response_model=WeeklyAnalyticsResponse)
def get_weekly_analytics(
    end_date: Optional[date] = Query(None, description="End date of week (default: today)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get weekly analytics for 7-day period"""
    service = AnalyticsService(db)
    
    analytics = service.get_weekly_analytics(current_user.id, end_date)
    
    return WeeklyAnalyticsResponse(
        start_date=analytics["start_date"],
        end_date=analytics["end_date"],
        total_tasks=analytics["total_tasks"],
        completed_tasks=analytics["completed_tasks"],
        skipped_tasks=analytics["skipped_tasks"],
        pending_tasks=analytics["pending_tasks"],
        completion_rate=analytics["completion_rate"],
        daily_breakdown=[DailyAnalyticsResponse(**day) for day in analytics["daily_breakdown"]]
    )


@router.get("/monthly", response_model=MonthlyAnalyticsResponse)
def get_monthly_analytics(
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get monthly analytics with category breakdown"""
    service = AnalyticsService(db)
    
    analytics = service.get_monthly_analytics(current_user.id, year, month)
    
    return MonthlyAnalyticsResponse(
        year=analytics["year"],
        month=analytics["month"],
        total_tasks=analytics["total_tasks"],
        completed_tasks=analytics["completed_tasks"],
        skipped_tasks=analytics["skipped_tasks"],
        pending_tasks=analytics["pending_tasks"],
        completion_rate=analytics["completion_rate"],
        category_breakdown=[CategoryStats(**cat) for cat in analytics["category_breakdown"]]
    )


@router.get("/insights", response_model=TaskInsightsResponse)
def get_task_insights(
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get task insights (most completed/skipped)"""
    service = AnalyticsService(db)
    
    insights = service.get_task_insights(current_user.id, start_date, end_date)
    
    return TaskInsightsResponse(
        most_completed=[TaskInsight(**item) for item in insights["most_completed"]],
        most_skipped=[TaskInsight(**item) for item in insights["most_skipped"]]
    )


@router.get("/heatmap", response_model=List[HeatmapData])
def get_activity_heatmap(
    start_date: date = Query(..., description="Start date"),
    end_date: date = Query(..., description="End date"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate activity heatmap for date range"""
    service = AnalyticsService(db)
    
    heatmap = service.generate_heatmap(current_user.id, start_date, end_date)
    
    return [HeatmapData(**day) for day in heatmap]
