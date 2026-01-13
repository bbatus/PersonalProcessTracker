"""
Goal service with user_id validation and authorization
"""

from datetime import datetime, date, timedelta
from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models.goal import Goal
from app.models.task import Task
from app.models.enums import GoalPeriod, TaskStatus
import logging

logger = logging.getLogger(__name__)


class GoalService:
    """Service for goal CRUD operations with user authorization"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def verify_goal_ownership(self, goal_id: UUID, user_id: UUID) -> Optional[Goal]:
        """
        Verify that a goal belongs to the user
        
        Args:
            goal_id: Goal UUID
            user_id: User UUID
            
        Returns:
            Goal if found and owned by user, None otherwise
        """
        goal = self.db.query(Goal).filter(
            and_(Goal.id == goal_id, Goal.user_id == user_id)
        ).first()
        
        return goal
    
    def create_goal(
        self,
        user_id: UUID,
        title: str,
        period: GoalPeriod,
        target_count: int,
        start_date: date,
        end_date: date,
        category_id: Optional[UUID] = None,
        description: Optional[str] = None
    ) -> Goal:
        """
        Create a new goal for user
        
        Args:
            user_id: User UUID
            title: Goal title
            period: Goal period (DAILY, WEEKLY, MONTHLY, YEARLY)
            target_count: Target count to achieve
            start_date: Goal start date
            end_date: Goal end date
            category_id: Optional category UUID
            description: Optional goal description
            
        Returns:
            Created goal
        """
        goal = Goal(
            user_id=user_id,
            title=title,
            period=period,
            target_count=target_count,
            current_count=0,
            start_date=start_date,
            end_date=end_date,
            category_id=category_id,
            description=description
        )
        
        self.db.add(goal)
        self.db.commit()
        self.db.refresh(goal)
        
        logger.info(f"Goal created: {goal.id} for user {user_id}")
        return goal
    
    def get_goals(
        self,
        user_id: UUID,
        period: Optional[GoalPeriod] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Goal]:
        """
        Get goals for user with optional filters, sorted by end_date
        
        Args:
            user_id: User UUID
            period: Optional filter by period
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return
            
        Returns:
            List of goals sorted by end_date
        """
        query = self.db.query(Goal).filter(Goal.user_id == user_id)
        
        if period:
            query = query.filter(Goal.period == period)
        
        # Order by end date (ascending - soonest first)
        query = query.order_by(Goal.end_date.asc())
        
        goals = query.offset(skip).limit(limit).all()
        
        return goals
    
    def get_goal(self, goal_id: UUID, user_id: UUID) -> Optional[Goal]:
        """
        Get a single goal with ownership verification
        
        Args:
            goal_id: Goal UUID
            user_id: User UUID
            
        Returns:
            Goal if found and owned by user, None otherwise
        """
        return self.verify_goal_ownership(goal_id, user_id)
    
    def get_goal_with_tasks(
        self,
        goal_id: UUID,
        user_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """
        Get goal with associated tasks and statistics
        
        Args:
            goal_id: Goal UUID
            user_id: User UUID
            
        Returns:
            Dictionary with goal, tasks, and stats, or None if not found
        """
        goal = self.verify_goal_ownership(goal_id, user_id)
        
        if not goal:
            return None
        
        # Get tasks for this goal
        tasks = self.db.query(Task).filter(
            Task.goal_id == goal_id,
            Task.user_id == user_id
        ).order_by(Task.scheduled_date.desc()).all()
        
        # Calculate statistics
        total_tasks = len(tasks)
        completed_tasks = sum(1 for t in tasks if t.status == TaskStatus.DONE)
        pending_tasks = sum(1 for t in tasks if t.status == TaskStatus.PENDING)
        skipped_tasks = sum(1 for t in tasks if t.status == TaskStatus.SKIPPED)
        
        progress_percentage = (goal.current_count / goal.target_count * 100) if goal.target_count > 0 else 0
        
        return {
            "goal": goal,
            "tasks": tasks,
            "stats": {
                "total": total_tasks,
                "completed": completed_tasks,
                "pending": pending_tasks,
                "skipped": skipped_tasks,
                "progress_percentage": round(progress_percentage, 1)
            }
        }
    
    def update_goal(
        self,
        goal_id: UUID,
        user_id: UUID,
        title: Optional[str] = None,
        description: Optional[str] = None,
        target_count: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        category_id: Optional[UUID] = None
    ) -> Tuple[Optional[Goal], Optional[str]]:
        """
        Update a goal with ownership verification
        
        Args:
            goal_id: Goal UUID
            user_id: User UUID
            title: Optional new title
            description: Optional new description
            target_count: Optional new target count
            start_date: Optional new start date
            end_date: Optional new end date
            category_id: Optional new category
            
        Returns:
            Tuple of (Goal, error_message). Goal is None if update failed.
        """
        goal = self.verify_goal_ownership(goal_id, user_id)
        
        if not goal:
            return None, "Goal not found or access denied"
        
        # Update fields if provided
        if title is not None:
            goal.title = title
        if description is not None:
            goal.description = description
        if target_count is not None:
            goal.target_count = target_count
        if start_date is not None:
            goal.start_date = start_date
        if end_date is not None:
            goal.end_date = end_date
        if category_id is not None:
            goal.category_id = category_id
        
        # Update timestamp
        goal.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(goal)
        
        logger.info(f"Goal updated: {goal.id}")
        return goal, None
    
    def delete_goal(self, goal_id: UUID, user_id: UUID) -> Tuple[bool, Optional[str]]:
        """
        Delete a goal with ownership verification
        
        Args:
            goal_id: Goal UUID
            user_id: User UUID
            
        Returns:
            Tuple of (success, error_message)
        """
        goal = self.verify_goal_ownership(goal_id, user_id)
        
        if not goal:
            return False, "Goal not found or access denied"
        
        self.db.delete(goal)
        self.db.commit()
        
        logger.info(f"Goal deleted: {goal_id}")
        return True, None
    
    def calculate_progress(self, goal_id: UUID, user_id: UUID) -> Tuple[Optional[float], Optional[str]]:
        """
        Calculate goal progress percentage
        
        Args:
            goal_id: Goal UUID
            user_id: User UUID
            
        Returns:
            Tuple of (progress_percentage, error_message)
        """
        goal = self.verify_goal_ownership(goal_id, user_id)
        
        if not goal:
            return None, "Goal not found or access denied"
        
        if goal.target_count == 0:
            return 0.0, None
        
        progress = (goal.current_count / goal.target_count) * 100
        return min(progress, 100.0), None
    
    def increment_goal_count(self, goal_id: UUID, user_id: UUID, amount: int = 1) -> Tuple[Optional[Goal], Optional[str]]:
        """
        Increment goal current count
        
        Args:
            goal_id: Goal UUID
            user_id: User UUID
            amount: Amount to increment (default 1)
            
        Returns:
            Tuple of (Goal, error_message)
        """
        goal = self.verify_goal_ownership(goal_id, user_id)
        
        if not goal:
            return None, "Goal not found or access denied"
        
        goal.current_count += amount
        goal.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(goal)
        
        logger.info(f"Goal count incremented: {goal_id} by {amount}")
        return goal, None
    
    def check_deadlines(self, user_id: UUID, days_threshold: int = 5) -> List[Goal]:
        """
        Get goals approaching deadline (within threshold days)
        
        Args:
            user_id: User UUID
            days_threshold: Number of days to look ahead (default 5)
            
        Returns:
            List of goals approaching deadline
        """
        today = date.today()
        threshold_date = today + timedelta(days=days_threshold)
        
        goals = self.db.query(Goal).filter(
            and_(
                Goal.user_id == user_id,
                Goal.end_date >= today,
                Goal.end_date <= threshold_date,
                Goal.current_count < Goal.target_count
            )
        ).order_by(Goal.end_date.asc()).all()
        
        return goals
    
    def mark_completed(self, goal_id: UUID, user_id: UUID) -> Tuple[Optional[Goal], Optional[str]]:
        """
        Mark goal as completed (current_count == target_count)
        
        Args:
            goal_id: Goal UUID
            user_id: User UUID
            
        Returns:
            Tuple of (Goal, error_message)
        """
        goal = self.verify_goal_ownership(goal_id, user_id)
        
        if not goal:
            return None, "Goal not found or access denied"
        
        goal.current_count = goal.target_count
        goal.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(goal)
        
        logger.info(f"Goal marked completed: {goal_id}")
        return goal, None
    
    def mark_failed(self, goal_id: UUID, user_id: UUID) -> Tuple[Optional[Goal], Optional[str]]:
        """
        Mark goal as failed (end_date passed, current < target)
        This is typically called by a background task
        
        Args:
            goal_id: Goal UUID
            user_id: User UUID
            
        Returns:
            Tuple of (Goal, error_message)
        """
        goal = self.verify_goal_ownership(goal_id, user_id)
        
        if not goal:
            return None, "Goal not found or access denied"
        
        # Just log it - we don't have a status field, but we can track it via current_count < target_count
        logger.info(f"Goal failed: {goal_id} - {goal.current_count}/{goal.target_count}")
        return goal, None


def get_goal_service(db: Session) -> GoalService:
    """Factory function to create GoalService instance"""
    return GoalService(db)
