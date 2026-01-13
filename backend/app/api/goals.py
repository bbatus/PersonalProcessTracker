"""
Goal API endpoints with authorization
"""

from datetime import date, datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.models.enums import GoalPeriod
from app.services.goal_service import GoalService

router = APIRouter(prefix="/api/goals", tags=["goals"])


# Pydantic schemas
class GoalCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    period: GoalPeriod
    target_count: int = Field(..., ge=1)
    start_date: date
    end_date: date
    category_id: Optional[UUID] = None


class GoalUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    target_count: Optional[int] = Field(None, ge=1)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    category_id: Optional[UUID] = None


class GoalResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    description: Optional[str]
    period: GoalPeriod
    target_count: int
    current_count: int
    start_date: date
    end_date: date
    category_id: Optional[UUID]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class GoalProgressResponse(BaseModel):
    goal: GoalResponse
    progress_percentage: float


class GoalWithTasksResponse(BaseModel):
    goal: GoalResponse
    tasks: List[Dict[str, Any]]
    stats: Dict[str, Any]


@router.post("", response_model=GoalResponse, status_code=201)
def create_goal(
    goal_data: GoalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new goal for the authenticated user"""
    service = GoalService(db)
    
    goal = service.create_goal(
        user_id=current_user.id,
        title=goal_data.title,
        period=goal_data.period,
        target_count=goal_data.target_count,
        start_date=goal_data.start_date,
        end_date=goal_data.end_date,
        category_id=goal_data.category_id,
        description=goal_data.description
    )
    
    return goal


@router.get("", response_model=List[GoalResponse])
def list_goals(
    period: Optional[GoalPeriod] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List goals for the authenticated user"""
    service = GoalService(db)
    
    goals = service.get_goals(
        user_id=current_user.id,
        period=period,
        skip=skip,
        limit=limit
    )
    
    return goals


@router.get("/deadlines", response_model=List[GoalResponse])
def get_goals_approaching_deadline(
    days: int = Query(5, ge=1, le=30),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get goals approaching deadline"""
    service = GoalService(db)
    
    goals = service.check_deadlines(current_user.id, days_threshold=days)
    
    return goals


@router.get("/{goal_id}", response_model=GoalResponse)
def get_goal(
    goal_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific goal with ownership verification"""
    service = GoalService(db)
    
    goal = service.get_goal(goal_id, current_user.id)
    
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    return goal


@router.get("/{goal_id}/progress", response_model=GoalProgressResponse)
def get_goal_progress(
    goal_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get goal progress with ownership verification"""
    service = GoalService(db)
    
    goal = service.get_goal(goal_id, current_user.id)
    
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    progress, error = service.calculate_progress(goal_id, current_user.id)
    
    if error:
        raise HTTPException(status_code=404, detail=error)
    
    return GoalProgressResponse(
        goal=goal,
        progress_percentage=progress
    )


@router.get("/{goal_id}/tasks", response_model=GoalWithTasksResponse)
def get_goal_with_tasks(
    goal_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get goal with all associated tasks and statistics"""
    service = GoalService(db)
    
    result = service.get_goal_with_tasks(goal_id, current_user.id)
    
    if not result:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    # Convert tasks to dict for response
    tasks_dict = [
        {
            "id": str(task.id),
            "title": task.title,
            "status": task.status.value,
            "scheduled_date": task.scheduled_date.isoformat(),
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "description": task.description,
            "notes": task.notes
        }
        for task in result["tasks"]
    ]
    
    return GoalWithTasksResponse(
        goal=result["goal"],
        tasks=tasks_dict,
        stats=result["stats"]
    )


@router.put("/{goal_id}", response_model=GoalResponse)
def update_goal(
    goal_id: UUID,
    goal_data: GoalUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a goal with ownership verification"""
    service = GoalService(db)
    
    goal, error = service.update_goal(
        goal_id=goal_id,
        user_id=current_user.id,
        title=goal_data.title,
        description=goal_data.description,
        target_count=goal_data.target_count,
        start_date=goal_data.start_date,
        end_date=goal_data.end_date,
        category_id=goal_data.category_id
    )
    
    if error:
        raise HTTPException(status_code=404, detail=error)
    
    return goal


@router.delete("/{goal_id}", status_code=204)
def delete_goal(
    goal_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a goal with ownership verification"""
    service = GoalService(db)
    
    success, error = service.delete_goal(goal_id, current_user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail=error)
    
    return None


class IncrementRequest(BaseModel):
    amount: int = Field(1, ge=1)


@router.patch("/{goal_id}/increment", response_model=GoalResponse)
def increment_goal(
    goal_id: UUID,
    increment_data: IncrementRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Increment goal count"""
    service = GoalService(db)
    
    goal, error = service.increment_goal_count(goal_id, current_user.id, increment_data.amount)
    
    if error:
        raise HTTPException(status_code=404, detail=error)
    
    return goal
