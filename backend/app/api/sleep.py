"""
Sleep API endpoints with authorization
"""

from datetime import date, datetime, time
from typing import List, Optional, Dict
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.services.sleep_service import SleepService

router = APIRouter(prefix="/api/sleep", tags=["sleep"])


# Pydantic schemas
class SleepLogCreate(BaseModel):
    date: date
    sleep_time: time
    wake_time: time
    quality_score: Optional[int] = Field(None, ge=1, le=10)
    notes: Optional[str] = None


class SleepLogUpdate(BaseModel):
    date: Optional[date] = None
    sleep_time: Optional[time] = None
    wake_time: Optional[time] = None
    quality_score: Optional[int] = Field(None, ge=1, le=10)
    notes: Optional[str] = None


class SleepLogResponse(BaseModel):
    id: UUID
    user_id: UUID
    date: date
    sleep_time: time
    wake_time: time
    duration_hours: float
    quality_score: Optional[int]
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


@router.post("", response_model=SleepLogResponse, status_code=201)
def create_sleep_log(
    sleep_data: SleepLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new sleep log for the authenticated user"""
    service = SleepService(db)
    
    sleep_log = service.create_sleep_log(
        user_id=current_user.id,
        date=sleep_data.date,
        sleep_time=sleep_data.sleep_time,
        wake_time=sleep_data.wake_time,
        quality_score=sleep_data.quality_score,
        notes=sleep_data.notes
    )
    
    return sleep_log


@router.get("", response_model=List[SleepLogResponse])
def list_sleep_logs(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List sleep logs for the authenticated user"""
    service = SleepService(db)
    
    sleep_logs = service.get_sleep_logs(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date,
        skip=skip,
        limit=limit
    )
    
    return sleep_logs


@router.get("/statistics", response_model=Dict)
def get_sleep_statistics(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get sleep statistics for the authenticated user"""
    service = SleepService(db)
    
    stats = service.get_sleep_statistics(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )
    
    return stats


@router.get("/{sleep_log_id}", response_model=SleepLogResponse)
def get_sleep_log(
    sleep_log_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific sleep log with ownership verification"""
    service = SleepService(db)
    
    sleep_log = service.get_sleep_log(sleep_log_id, current_user.id)
    
    if not sleep_log:
        raise HTTPException(status_code=404, detail="Sleep log not found")
    
    return sleep_log


@router.put("/{sleep_log_id}", response_model=SleepLogResponse)
def update_sleep_log(
    sleep_log_id: UUID,
    sleep_data: SleepLogUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a sleep log with ownership verification"""
    service = SleepService(db)
    
    sleep_log, error = service.update_sleep_log(
        sleep_log_id=sleep_log_id,
        user_id=current_user.id,
        date=sleep_data.date,
        sleep_time=sleep_data.sleep_time,
        wake_time=sleep_data.wake_time,
        quality_score=sleep_data.quality_score,
        notes=sleep_data.notes
    )
    
    if error:
        raise HTTPException(status_code=404, detail=error)
    
    return sleep_log


@router.delete("/{sleep_log_id}", status_code=204)
def delete_sleep_log(
    sleep_log_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a sleep log with ownership verification"""
    service = SleepService(db)
    
    success, error = service.delete_sleep_log(sleep_log_id, current_user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail=error)
    
    return None
