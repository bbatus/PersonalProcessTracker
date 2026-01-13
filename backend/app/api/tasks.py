"""
Task API endpoints with authorization
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
from app.models.enums import TaskStatus
from app.services.task_service import TaskService

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


# Pydantic schemas
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = None
    scheduled_date: date
    category_id: Optional[UUID] = None
    goal_id: Optional[UUID] = None  # NEW
    estimated_duration: Optional[int] = Field(None, ge=1)  # Minutes


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    notes: Optional[str] = None
    scheduled_date: Optional[date] = None
    category_id: Optional[UUID] = None
    goal_id: Optional[UUID] = None  # NEW
    estimated_duration: Optional[int] = Field(None, ge=1)
    status: Optional[TaskStatus] = None


class TaskResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    description: Optional[str]
    notes: Optional[str]
    status: TaskStatus
    scheduled_date: date
    completed_at: Optional[datetime]
    estimated_duration: Optional[int]
    category_id: Optional[UUID]
    habit_id: Optional[UUID]
    goal_id: Optional[UUID]  # NEW
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    tasks: List[TaskResponse]
    total: int
    skip: int
    limit: int


@router.post("", response_model=TaskResponse, status_code=201)
def create_task(
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new task for the authenticated user"""
    service = TaskService(db)
    
    try:
        task = service.create_task(
            user_id=current_user.id,
            title=task_data.title,
            scheduled_date=task_data.scheduled_date,
            category_id=task_data.category_id,
            goal_id=task_data.goal_id,  # NEW
            description=task_data.description,
            estimated_duration=task_data.estimated_duration
        )
        
        return task
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=TaskListResponse)
def list_tasks(
    scheduled_date: Optional[date] = Query(None),
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    status: Optional[TaskStatus] = Query(None),
    category_id: Optional[UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List tasks for the authenticated user with optional filters"""
    service = TaskService(db)
    
    tasks = service.get_tasks(
        user_id=current_user.id,
        scheduled_date=scheduled_date,
        start_date=start_date,
        end_date=end_date,
        status=status,
        category_id=category_id,
        skip=skip,
        limit=limit
    )
    
    # Get total count for pagination
    from sqlalchemy import func, and_
    from app.models.task import Task
    
    query = db.query(func.count(Task.id)).filter(Task.user_id == current_user.id)
    if scheduled_date:
        query = query.filter(Task.scheduled_date == scheduled_date)
    if start_date:
        query = query.filter(Task.scheduled_date >= start_date)
    if end_date:
        query = query.filter(Task.scheduled_date <= end_date)
    if status:
        query = query.filter(Task.status == status)
    if category_id:
        query = query.filter(Task.category_id == category_id)
    
    total = query.scalar()
    
    return TaskListResponse(
        tasks=tasks,
        total=total,
        skip=skip,
        limit=limit
    )


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific task with ownership verification"""
    service = TaskService(db)
    
    task = service.get_task(task_id, current_user.id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return task


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: UUID,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a task with ownership verification"""
    service = TaskService(db)
    
    task, error = service.update_task(
        task_id=task_id,
        user_id=current_user.id,
        title=task_data.title,
        description=task_data.description,
        notes=task_data.notes,
        scheduled_date=task_data.scheduled_date,
        category_id=task_data.category_id,
        goal_id=task_data.goal_id,  # NEW
        estimated_duration=task_data.estimated_duration,
        status=task_data.status
    )
    
    if error:
        raise HTTPException(status_code=404, detail=error)
    
    return task


@router.delete("/{task_id}", status_code=204)
def delete_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a task with ownership verification"""
    service = TaskService(db)
    
    success, error = service.delete_task(task_id, current_user.id)
    
    if not success:
        raise HTTPException(status_code=404, detail=error)
    
    return None


@router.patch("/{task_id}/done", response_model=TaskResponse)
def mark_task_done(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a task as done"""
    service = TaskService(db)
    
    task, error = service.mark_done(task_id, current_user.id)
    
    if error:
        raise HTTPException(status_code=404, detail=error)
    
    return task


@router.patch("/{task_id}/skip", response_model=TaskResponse)
def mark_task_skipped(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a task as skipped"""
    service = TaskService(db)
    
    task, error = service.mark_skipped(task_id, current_user.id)
    
    if error:
        raise HTTPException(status_code=404, detail=error)
    
    return task


@router.patch("/{task_id}/reopen", response_model=TaskResponse)
def reopen_task(
    task_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Reopen a done or skipped task"""
    service = TaskService(db)
    
    task, error = service.reopen_task(task_id, current_user.id)
    
    if error:
        raise HTTPException(status_code=404, detail=error)
    
    return task


class PostponeRequest(BaseModel):
    days: int = Field(1, ge=1, le=365)


@router.patch("/{task_id}/postpone", response_model=TaskResponse)
def postpone_task(
    task_id: UUID,
    postpone_data: PostponeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Postpone a task by specified number of days"""
    service = TaskService(db)
    
    task, error = service.postpone_task(task_id, current_user.id, postpone_data.days)
    
    if error:
        raise HTTPException(status_code=404, detail=error)
    
    return task
