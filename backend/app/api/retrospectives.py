"""
Retrospective API endpoints with authorization
"""

from datetime import date, datetime
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.services.retrospective_service import RetrospectiveService

router = APIRouter(prefix="/api/retrospectives", tags=["retrospectives"])


# Pydantic schemas
class RetrospectiveCreate(BaseModel):
    month: date  # YYYY-MM-01 format
    what_went_well: str = Field(..., min_length=1)
    what_went_bad: str = Field(..., min_length=1)
    what_to_change: str = Field(..., min_length=1)
    average_mood: Optional[float] = Field(None, ge=1, le=10)


class RetrospectiveResponse(BaseModel):
    id: UUID
    user_id: UUID
    month: date
    success_rate: Optional[float]
    total_tasks: Optional[int]
    completed_tasks: Optional[int]
    what_went_well: str
    what_went_bad: str
    what_to_change: str
    average_mood: Optional[float]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MoodLogCreate(BaseModel):
    log_date: date
    mood_score: int = Field(..., ge=1, le=10)
    notes: Optional[str] = None


class MoodLogResponse(BaseModel):
    id: UUID
    user_id: UUID
    date: date
    mood_score: int
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.post("", response_model=RetrospectiveResponse, status_code=201)
def create_or_update_retrospective(
    retro_data: RetrospectiveCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create or update retrospective (upsert)"""
    service = RetrospectiveService(db)
    
    retrospective, error = service.create_or_update_retrospective(
        user_id=current_user.id,
        month=retro_data.month,
        what_went_well=retro_data.what_went_well,
        what_went_bad=retro_data.what_went_bad,
        what_to_change=retro_data.what_to_change,
        average_mood=retro_data.average_mood
    )
    
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    return retrospective


@router.get("", response_model=List[RetrospectiveResponse])
def list_retrospectives(
    skip: int = Query(0, ge=0),
    limit: int = Query(12, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all retrospectives for the authenticated user"""
    service = RetrospectiveService(db)
    
    retrospectives = service.get_retrospectives(
        user_id=current_user.id,
        skip=skip,
        limit=limit
    )
    
    return retrospectives


@router.get("/{month}", response_model=RetrospectiveResponse)
def get_retrospective_by_month(
    month: date,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get retrospective by month"""
    service = RetrospectiveService(db)
    
    retrospective = service.get_retrospective(current_user.id, month)
    
    if not retrospective:
        raise HTTPException(status_code=404, detail="Retrospective not found for this month")
    
    return retrospective


@router.post("/mood", response_model=MoodLogResponse, status_code=201)
def log_mood(
    mood_data: MoodLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Log daily mood"""
    service = RetrospectiveService(db)
    
    mood_log, error = service.log_mood(
        user_id=current_user.id,
        log_date=mood_data.log_date,
        mood_score=mood_data.mood_score,
        notes=mood_data.notes
    )
    
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    return mood_log


@router.get("/mood/logs", response_model=List[MoodLogResponse])
def get_mood_logs(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get mood logs for date range"""
    service = RetrospectiveService(db)
    
    mood_logs = service.get_mood_logs(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )
    
    return mood_logs
