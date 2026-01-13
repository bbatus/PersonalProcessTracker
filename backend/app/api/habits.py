"""
Habit API endpoints with authorization
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
from app.models.enums import HabitFrequency
from app.services.habit_service import HabitService

router = APIRouter(prefix="/api/habits", tags=["habits"])


# Pydantic schemas
class HabitCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    frequency: HabitFrequency
    target_days: Optional[int] = Field(None, ge=1, le=7)  # For WEEKLY habits
    duration_days: Optional[int] = Field(None, ge=1, le=365)  # Number of days to generate tasks
    start_date: Optional[date] = None  # Start date for habit (defaults to today)


class HabitUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    frequency: Optional[HabitFrequency] = None
    target_days: Optional[int] = Field(None, ge=1, le=7)


class HabitResponse(BaseModel):
    id: UUID
    user_id: UUID
    name: str
    frequency: HabitFrequency
    target_days: Optional[int]
    duration_days: Optional[int]
    start_date: Optional[date]
    current_streak: int
    longest_streak: int
    last_completed: Optional[date]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class HabitLogCreate(BaseModel):
    completed_date: date
    notes: Optional[str] = None


class HabitLogResponse(BaseModel):
    id: UUID
    habit_id: UUID
    completed_date: date
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class StreakResponse(BaseModel):
    habit: HabitResponse
    current_streak: int
    longest_streak: int


@router.post("", response_model=HabitResponse, status_code=201)
def create_habit(
    habit_data: HabitCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new habit for the authenticated user"""
    service = HabitService(db)
    
    habit = service.create_habit(
        user_id=current_user.id,
        name=habit_data.name,
        frequency=habit_data.frequency,
        target_days=habit_data.target_days,
        duration_days=habit_data.duration_days,
        start_date=habit_data.start_date
    )
    
    return habit


@router.get("", response_model=List[HabitResponse])
def list_habits(
    frequency: Optional[HabitFrequency] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List habits for the authenticated user"""
    service = HabitService(db)
    
    habits = service.get_habits(
        user_id=current_user.id,
        frequency=frequency,
        skip=skip,
        limit=limit
    )
    
    return habits


@router.get("/at-risk", response_model=List[HabitResponse])
def get_at_risk_habits(
    days: int = Query(3, ge=1, le=30),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get habits at risk (not completed for specified days)"""
    service = HabitService(db)
    
    habits = service.check_at_risk_habits(current_user.id, days_threshold=days)
    
    return habits


@router.get("/{habit_id}", response_model=HabitResponse)
def get_habit(
    habit_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific habit with ownership verification"""
    service = HabitService(db)
    
    habit = service.get_habit(habit_id, current_user.id)
    
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    
    return habit


@router.get("/{habit_id}/streak", response_model=StreakResponse)
def get_habit_streak(
    habit_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get habit streak information"""
    service = HabitService(db)
    
    habit = service.get_habit(habit_id, current_user.id)
    
    if not habit:
        raise HTTPException(status_code=404, detail="Habit not found")
    
    # Recalculate streak to ensure it's up to date
    streak, error = service.calculate_streak(habit_id, current_user.id)
    
    if error:
        raise HTTPException(status_code=404, detail=error)
    
    # Refresh habit to get updated values
    db.refresh(habit)
    
    return StreakResponse(
        habit=habit,
        current_streak=habit.current_streak,
        longest_streak=habit.longest_streak
    )


@router.put("/{habit_id}", response_model=HabitResponse)
def update_habit(
    habit_id: UUID,
    habit_data: HabitUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a habit with ownership verification"""
    service = HabitService(db)
    
    habit, error = service.update_habit(
        habit_id=habit_id,
        user_id=current_user.id,
        name=habit_data.name,
        frequency=habit_data.frequency,
        target_days=habit_data.target_days
    )
    
    if error:
        raise HTTPException(status_code=404, detail=error)
    
    return habit


@router.delete("/{habit_id}", status_code=204)
def delete_habit(
    habit_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a habit with ownership verification"""
    service = HabitService(db)
    
    success, error = service.delete_habit(habit_id, current_user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail=error)
    
    return None


@router.post("/{habit_id}/log", response_model=HabitLogResponse, status_code=201)
def log_habit_completion(
    habit_id: UUID,
    log_data: HabitLogCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Log habit completion"""
    service = HabitService(db)
    
    log, error = service.log_completion(
        habit_id=habit_id,
        user_id=current_user.id,
        completed_date=log_data.completed_date,
        notes=log_data.notes
    )
    
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    return log
