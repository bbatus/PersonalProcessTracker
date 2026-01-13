"""
Task service with user_id validation and authorization
"""

from datetime import datetime, date, timedelta
from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.task import Task
from app.models.goal import Goal
from app.models.enums import TaskStatus
from app.models.user import User
import logging

logger = logging.getLogger(__name__)


class TaskService:
    """Service for task CRUD operations with user authorization"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def verify_task_ownership(self, task_id: UUID, user_id: UUID) -> Optional[Task]:
        """
        Verify that a task belongs to the user
        
        Args:
            task_id: Task UUID
            user_id: User UUID
            
        Returns:
            Task if found and owned by user, None otherwise
        """
        task = self.db.query(Task).filter(
            and_(Task.id == task_id, Task.user_id == user_id)
        ).first()
        
        return task
    
    def create_task(
        self,
        user_id: UUID,
        title: str,
        scheduled_date: date,
        category_id: Optional[UUID] = None,
        goal_id: Optional[UUID] = None,
        description: Optional[str] = None,
        estimated_duration: Optional[int] = None
    ) -> Task:
        """
        Create a new task for user
        
        Args:
            user_id: User UUID
            title: Task title
            scheduled_date: Date task is scheduled for
            category_id: Optional category UUID
            goal_id: Optional goal UUID (must belong to same user)
            description: Optional task description
            estimated_duration: Optional estimated duration in minutes
            
        Returns:
            Created task
            
        Raises:
            ValueError: If goal_id is provided but goal doesn't exist or doesn't belong to user
        """
        # Validate goal ownership if goal_id provided
        if goal_id:
            goal = self.db.query(Goal).filter(
                Goal.id == goal_id,
                Goal.user_id == user_id
            ).first()
            
            if not goal:
                raise ValueError("Goal not found or access denied")
        
        task = Task(
            user_id=user_id,
            title=title,
            scheduled_date=scheduled_date,
            category_id=category_id,
            goal_id=goal_id,
            description=description,
            estimated_duration=estimated_duration,
            status=TaskStatus.PENDING
        )
        
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        
        logger.info(f"Task created: {task.id} for user {user_id}")
        return task
    
    def get_tasks(
        self,
        user_id: UUID,
        scheduled_date: Optional[date] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status: Optional[TaskStatus] = None,
        category_id: Optional[UUID] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Task]:
        """
        Get tasks for user with optional filters
        
        Args:
            user_id: User UUID
            scheduled_date: Optional filter by exact date
            start_date: Optional filter by start date (inclusive)
            end_date: Optional filter by end date (inclusive)
            status: Optional filter by status
            category_id: Optional filter by category
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return
            
        Returns:
            List of tasks
        """
        query = self.db.query(Task).filter(Task.user_id == user_id)
        
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
        
        # Order by scheduled date and created time
        query = query.order_by(Task.scheduled_date.asc(), Task.created_at.asc())
        
        tasks = query.offset(skip).limit(limit).all()
        
        return tasks
    
    def get_task(self, task_id: UUID, user_id: UUID) -> Optional[Task]:
        """
        Get a single task with ownership verification
        
        Args:
            task_id: Task UUID
            user_id: User UUID
            
        Returns:
            Task if found and owned by user, None otherwise
        """
        return self.verify_task_ownership(task_id, user_id)
    
    def update_task(
        self,
        task_id: UUID,
        user_id: UUID,
        title: Optional[str] = None,
        description: Optional[str] = None,
        notes: Optional[str] = None,
        scheduled_date: Optional[date] = None,
        category_id: Optional[UUID] = None,
        goal_id: Optional[UUID] = None,
        estimated_duration: Optional[int] = None,
        status: Optional[TaskStatus] = None
    ) -> Tuple[Optional[Task], Optional[str]]:
        """
        Update a task with ownership verification.
        Handles goal changes for completed tasks.
        
        Args:
            task_id: Task UUID
            user_id: User UUID
            title: Optional new title
            description: Optional new description
            notes: Optional new notes
            scheduled_date: Optional new scheduled date
            category_id: Optional new category
            goal_id: Optional new goal (validates ownership)
            estimated_duration: Optional new duration
            status: Optional new status
            
        Returns:
            Tuple of (Task, error_message). Task is None if update failed.
        """
        task = self._get_task_with_lock(task_id, user_id)
        
        if not task:
            return None, "Task not found or access denied"
        
        # Validate new goal ownership if provided (and not explicitly set to None)
        if goal_id is not None and goal_id != "":
            goal = self.db.query(Goal).filter(
                Goal.id == goal_id,
                Goal.user_id == user_id
            ).first()
            
            if not goal:
                return None, "Goal not found or access denied"
        
        try:
            # Handle goal change for completed tasks
            # This includes: goal A -> goal B, goal A -> no goal, no goal -> goal A
            if task.status == TaskStatus.DONE:
                old_goal_id = task.goal_id
                new_goal_id = goal_id if goal_id != "" else None
                
                # Only process if goal actually changed
                if old_goal_id != new_goal_id:
                    # Decrement old goal if it exists
                    if old_goal_id:
                        self._decrement_goal_progress(old_goal_id, user_id)
                    
                    # Increment new goal if it exists
                    if new_goal_id:
                        self._increment_goal_progress(new_goal_id, user_id)
            
            # Update fields if provided
            if title is not None:
                task.title = title
            if description is not None:
                task.description = description
            if notes is not None:
                task.notes = notes
            if scheduled_date is not None:
                task.scheduled_date = scheduled_date
            if category_id is not None:
                task.category_id = category_id
            # Update goal_id - handle both explicit None and empty string
            if goal_id is not None:
                task.goal_id = goal_id if goal_id != "" else None
            if estimated_duration is not None:
                task.estimated_duration = estimated_duration
            if status is not None:
                task.status = status
            
            # Update timestamp
            task.updated_at = datetime.utcnow()
            
            self.db.commit()
            self.db.refresh(task)
            
            logger.info(f"Task updated: {task.id}")
            return task, None
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update task: {str(e)}")
            return None, f"Failed to update task: {str(e)}"
    
    def delete_task(self, task_id: UUID, user_id: UUID) -> Tuple[bool, Optional[str]]:
        """
        Delete a task with ownership verification.
        If task was DONE and linked to a goal, decrement goal progress.
        
        Args:
            task_id: Task UUID
            user_id: User UUID
            
        Returns:
            Tuple of (success, error_message)
        """
        task = self._get_task_with_lock(task_id, user_id)
        
        if not task:
            return False, "Task not found or access denied"
        
        try:
            # Decrement goal if task was done and linked
            if task.goal_id and task.status == TaskStatus.DONE:
                self._decrement_goal_progress(task.goal_id, user_id)
            
            self.db.delete(task)
            self.db.commit()
            
            logger.info(f"Task deleted: {task_id}")
            return True, None
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete task: {str(e)}")
            return False, f"Failed to delete task: {str(e)}"
    
    def _get_task_with_lock(self, task_id: UUID, user_id: UUID) -> Optional[Task]:
        """
        Get task with row-level lock for safe updates
        
        Args:
            task_id: Task UUID
            user_id: User UUID
            
        Returns:
            Task if found and owned by user, None otherwise
        """
        return self.db.query(Task).filter(
            Task.id == task_id,
            Task.user_id == user_id
        ).with_for_update().first()
    
    def _increment_goal_progress(self, goal_id: UUID, user_id: UUID):
        """
        Increment goal current_count by 1 (with bounds checking)
        
        Args:
            goal_id: Goal UUID
            user_id: User UUID
        """
        goal = self.db.query(Goal).filter(
            Goal.id == goal_id,
            Goal.user_id == user_id
        ).with_for_update().first()
        
        if goal:
            # Ensure we don't exceed target_count
            goal.current_count = min(goal.current_count + 1, goal.target_count)
            goal.updated_at = datetime.utcnow()
            logger.info(f"Goal {goal_id} progress incremented to {goal.current_count}/{goal.target_count}")
    
    def _decrement_goal_progress(self, goal_id: UUID, user_id: UUID):
        """
        Decrement goal current_count by 1 (with bounds checking)
        
        Args:
            goal_id: Goal UUID
            user_id: User UUID
        """
        goal = self.db.query(Goal).filter(
            Goal.id == goal_id,
            Goal.user_id == user_id
        ).with_for_update().first()
        
        if goal:
            # Ensure we don't go below 0
            goal.current_count = max(goal.current_count - 1, 0)
            goal.updated_at = datetime.utcnow()
            logger.info(f"Goal {goal_id} progress decremented to {goal.current_count}/{goal.target_count}")
    
    def mark_done(self, task_id: UUID, user_id: UUID) -> Tuple[Optional[Task], Optional[str]]:
        """
        Mark task as done. If it's a habit task, also log habit completion.
        If task is linked to a goal, increment goal progress.
        
        Args:
            task_id: Task UUID
            user_id: User UUID
            
        Returns:
            Tuple of (Task, error_message)
        """
        task = self._get_task_with_lock(task_id, user_id)
        
        if not task:
            return None, "Task not found or access denied"
        
        # Store previous status for goal update logic
        previous_status = task.status
        
        try:
            task.status = TaskStatus.DONE
            task.completed_at = datetime.utcnow()
            task.updated_at = datetime.utcnow()
            
            # Update goal progress if linked and wasn't already done
            if task.goal_id and previous_status != TaskStatus.DONE:
                self._increment_goal_progress(task.goal_id, user_id)
            
            # If this is a habit task, also log the habit completion
            if task.habit_id:
                from app.services.habit_service import HabitService
                habit_service = HabitService(self.db)
                
                # Log completion for the scheduled date
                log, error = habit_service.log_completion(
                    habit_id=task.habit_id,
                    user_id=user_id,
                    completed_date=task.scheduled_date,
                    notes=f"Completed via task: {task.title}"
                )
                
                if error and "already logged" not in error.lower():
                    logger.warning(f"Failed to log habit completion for task {task_id}: {error}")
                else:
                    logger.info(f"Habit completion logged for task {task_id}")
            
            self.db.commit()
            self.db.refresh(task)
            
            logger.info(f"Task marked done: {task_id}")
            return task, None
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to mark task as done: {str(e)}")
            return None, f"Failed to mark task as done: {str(e)}"
    
    def mark_skipped(self, task_id: UUID, user_id: UUID) -> Tuple[Optional[Task], Optional[str]]:
        """
        Mark task as skipped
        
        Args:
            task_id: Task UUID
            user_id: User UUID
            
        Returns:
            Tuple of (Task, error_message)
        """
        task = self.verify_task_ownership(task_id, user_id)
        
        if not task:
            return None, "Task not found or access denied"
        
        task.status = TaskStatus.SKIPPED
        task.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(task)
        
        logger.info(f"Task marked skipped: {task_id}")
        return task, None
    
    def reopen_task(self, task_id: UUID, user_id: UUID) -> Tuple[Optional[Task], Optional[str]]:
        """
        Reopen a done or skipped task.
        If task was DONE and linked to a goal, decrement goal progress.
        
        Args:
            task_id: Task UUID
            user_id: User UUID
            
        Returns:
            Tuple of (Task, error_message)
        """
        task = self._get_task_with_lock(task_id, user_id)
        
        if not task:
            return None, "Task not found or access denied"
        
        # Store previous status for goal update logic
        previous_status = task.status
        
        try:
            task.status = TaskStatus.PENDING
            task.completed_at = None
            task.updated_at = datetime.utcnow()
            
            # Decrement goal progress if was done and linked to goal
            if task.goal_id and previous_status == TaskStatus.DONE:
                self._decrement_goal_progress(task.goal_id, user_id)
            
            self.db.commit()
            self.db.refresh(task)
            
            logger.info(f"Task reopened: {task_id}")
            return task, None
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to reopen task: {str(e)}")
            return None, f"Failed to reopen task: {str(e)}"
    
    def postpone_task(self, task_id: UUID, user_id: UUID, days: int = 1) -> Tuple[Optional[Task], Optional[str]]:
        """
        Postpone task by specified number of days
        
        Args:
            task_id: Task UUID
            user_id: User UUID
            days: Number of days to postpone (default 1)
            
        Returns:
            Tuple of (Task, error_message)
        """
        task = self.verify_task_ownership(task_id, user_id)
        
        if not task:
            return None, "Task not found or access denied"
        
        task.scheduled_date = task.scheduled_date + timedelta(days=days)
        task.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(task)
        
        logger.info(f"Task postponed: {task_id} by {days} days")
        return task, None


def get_task_service(db: Session) -> TaskService:
    """Factory function to create TaskService instance"""
    return TaskService(db)
