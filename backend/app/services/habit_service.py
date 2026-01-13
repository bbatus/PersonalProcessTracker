"""
Habit service with user_id validation and authorization
"""

from datetime import datetime, date, timedelta
from typing import List, Optional, Tuple
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from sqlalchemy.exc import IntegrityError

from app.models.habit import Habit, HabitLog
from app.models.task import Task
from app.models.enums import HabitFrequency, TaskStatus
import logging

logger = logging.getLogger(__name__)


class HabitService:
    """Service for habit CRUD operations with user authorization"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def verify_habit_ownership(self, habit_id: UUID, user_id: UUID) -> Optional[Habit]:
        """
        Verify that a habit belongs to the user
        
        Args:
            habit_id: Habit UUID
            user_id: User UUID
            
        Returns:
            Habit if found and owned by user, None otherwise
        """
        habit = self.db.query(Habit).filter(
            and_(Habit.id == habit_id, Habit.user_id == user_id)
        ).first()
        
        return habit
    
    def create_habit(
        self,
        user_id: UUID,
        name: str,
        frequency: HabitFrequency,
        target_days: Optional[int] = None,
        duration_days: Optional[int] = None,
        start_date: Optional[date] = None
    ) -> Habit:
        """
        Create a new habit for user and auto-generate tasks if duration is specified
        
        Args:
            user_id: User UUID
            name: Habit name
            frequency: Habit frequency (DAILY, WEEKLY)
            target_days: Target days per week (for WEEKLY habits)
            duration_days: Number of days to generate tasks for
            start_date: Start date for habit (defaults to today)
            
        Returns:
            Created habit
        """
        # Default start_date to today if not provided
        if start_date is None:
            start_date = date.today()
        
        habit = Habit(
            user_id=user_id,
            name=name,
            frequency=frequency,
            target_days=target_days,
            duration_days=duration_days,
            start_date=start_date,
            current_streak=0,
            longest_streak=0,
            last_completed=None
        )
        
        self.db.add(habit)
        self.db.commit()
        self.db.refresh(habit)
        
        # Auto-generate tasks if duration_days is specified
        if duration_days and duration_days > 0:
            self._generate_habit_tasks(habit, start_date, duration_days)
        
        logger.info(f"Habit created: {habit.id} for user {user_id} with {duration_days or 0} days")
        return habit
    
    def _generate_habit_tasks(self, habit: Habit, start_date: date, duration_days: int) -> None:
        """
        Generate tasks for a habit (includes start_date, so if duration is 30, creates 30 tasks starting from start_date)
        
        Args:
            habit: Habit object
            start_date: Start date for tasks (inclusive)
            duration_days: Number of days to generate tasks for
        """
        tasks = []
        # Start from day 0 to include the start_date itself
        for day_offset in range(duration_days):
            task_date = start_date + timedelta(days=day_offset)
            task = Task(
                user_id=habit.user_id,
                habit_id=habit.id,
                title=habit.name,
                description=f"Daily habit: {habit.name}",
                status=TaskStatus.PENDING,
                scheduled_date=task_date,
                estimated_duration=30  # Default 30 minutes
            )
            tasks.append(task)
        
        # Bulk insert tasks
        self.db.bulk_save_objects(tasks)
        self.db.commit()
        
        logger.info(f"Generated {len(tasks)} tasks for habit {habit.id} from {start_date} for {duration_days} days")
    
    def get_habits(
        self,
        user_id: UUID,
        frequency: Optional[HabitFrequency] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Habit]:
        """
        Get habits for user with optional filters
        
        Args:
            user_id: User UUID
            frequency: Optional filter by frequency
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return
            
        Returns:
            List of habits
        """
        query = self.db.query(Habit).filter(Habit.user_id == user_id)
        
        if frequency:
            query = query.filter(Habit.frequency == frequency)
        
        # Order by current streak (descending) and name
        query = query.order_by(Habit.current_streak.desc(), Habit.name.asc())
        
        habits = query.offset(skip).limit(limit).all()
        
        return habits
    
    def get_habit(self, habit_id: UUID, user_id: UUID) -> Optional[Habit]:
        """
        Get a single habit with ownership verification
        
        Args:
            habit_id: Habit UUID
            user_id: User UUID
            
        Returns:
            Habit if found and owned by user, None otherwise
        """
        return self.verify_habit_ownership(habit_id, user_id)
    
    def update_habit(
        self,
        habit_id: UUID,
        user_id: UUID,
        name: Optional[str] = None,
        frequency: Optional[HabitFrequency] = None,
        target_days: Optional[int] = None
    ) -> Tuple[Optional[Habit], Optional[str]]:
        """
        Update a habit with ownership verification
        
        Args:
            habit_id: Habit UUID
            user_id: User UUID
            name: Optional new name
            frequency: Optional new frequency
            target_days: Optional new target days
            
        Returns:
            Tuple of (Habit, error_message). Habit is None if update failed.
        """
        habit = self.verify_habit_ownership(habit_id, user_id)
        
        if not habit:
            return None, "Habit not found or access denied"
        
        # Update fields if provided
        if name is not None:
            habit.name = name
        if frequency is not None:
            habit.frequency = frequency
        if target_days is not None:
            habit.target_days = target_days
        
        # Update timestamp
        habit.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(habit)
        
        logger.info(f"Habit updated: {habit.id}")
        return habit, None
    
    def delete_habit(self, habit_id: UUID, user_id: UUID) -> Tuple[bool, Optional[str]]:
        """
        Delete a habit with cascade log deletion and ownership verification
        
        Args:
            habit_id: Habit UUID
            user_id: User UUID
            
        Returns:
            Tuple of (success, error_message)
        """
        habit = self.verify_habit_ownership(habit_id, user_id)
        
        if not habit:
            return False, "Habit not found or access denied"
        
        # Cascade deletion is handled by SQLAlchemy relationship
        self.db.delete(habit)
        self.db.commit()
        
        logger.info(f"Habit deleted: {habit_id}")
        return True, None
    
    def log_completion(
        self,
        habit_id: UUID,
        user_id: UUID,
        completed_date: date,
        notes: Optional[str] = None
    ) -> Tuple[Optional[HabitLog], Optional[str]]:
        """
        Log habit completion with duplicate prevention
        
        Args:
            habit_id: Habit UUID
            user_id: User UUID
            completed_date: Date of completion
            notes: Optional notes
            
        Returns:
            Tuple of (HabitLog, error_message)
        """
        habit = self.verify_habit_ownership(habit_id, user_id)
        
        if not habit:
            return None, "Habit not found or access denied"
        
        # Create log entry
        log = HabitLog(
            habit_id=habit_id,
            completed_date=completed_date,
            notes=notes
        )
        
        try:
            self.db.add(log)
            
            # Update habit's last_completed
            habit.last_completed = completed_date
            habit.updated_at = datetime.utcnow()
            
            # Recalculate streak
            self.calculate_streak(habit_id, user_id)
            
            self.db.commit()
            self.db.refresh(log)
            
            logger.info(f"Habit completion logged: {habit_id} on {completed_date}")
            return log, None
            
        except IntegrityError:
            self.db.rollback()
            return None, "Habit already logged for this date"
    
    def calculate_streak(self, habit_id: UUID, user_id: UUID) -> Tuple[Optional[int], Optional[str]]:
        """
        Calculate current streak for habits based on their frequency
        
        Args:
            habit_id: Habit UUID
            user_id: User UUID
            
        Returns:
            Tuple of (streak_count, error_message)
        """
        habit = self.verify_habit_ownership(habit_id, user_id)
        
        if not habit:
            return None, "Habit not found or access denied"
        
        # Get all logs ordered by date descending
        logs = self.db.query(HabitLog).filter(
            HabitLog.habit_id == habit_id
        ).order_by(HabitLog.completed_date.desc()).all()
        
        if not logs:
            habit.current_streak = 0
            self.db.commit()
            return 0, None
        
        # Calculate streak based on frequency
        today = date.today()
        
        if habit.frequency == HabitFrequency.DAILY:
            # Check if today or yesterday was logged (streak is still active)
            if logs[0].completed_date < today - timedelta(days=1):
                # Streak is broken (last log was before yesterday)
                habit.current_streak = 0
                self.db.commit()
                return 0, None
            
            # Count consecutive days starting from the most recent log
            streak = 1  # Start with 1 for the first log
            expected_date = logs[0].completed_date - timedelta(days=1)
            
            # Check remaining logs for consecutive days
            for log in logs[1:]:
                if log.completed_date == expected_date:
                    streak += 1
                    expected_date = log.completed_date - timedelta(days=1)
                else:
                    # Gap found, stop counting
                    break
        
        elif habit.frequency == HabitFrequency.WEEKLY:
            # For weekly habits, count consecutive weeks
            # A week is considered complete if there's at least one log in that week
            streak = 0
            current_week_start = today - timedelta(days=today.weekday())  # Monday of current week
            
            for log in logs:
                log_week_start = log.completed_date - timedelta(days=log.completed_date.weekday())
                
                # Check if this log is in the expected week
                expected_week_start = current_week_start - timedelta(weeks=streak)
                
                if log_week_start == expected_week_start:
                    streak += 1
                elif log_week_start < expected_week_start:
                    # Gap found, stop counting
                    break
        
        elif habit.frequency == HabitFrequency.MONTHLY:
            # For monthly habits, count consecutive months
            streak = 0
            current_month = (today.year, today.month)
            
            for log in logs:
                log_month = (log.completed_date.year, log.completed_date.month)
                
                # Calculate expected month
                year = current_month[0]
                month = current_month[1] - streak
                while month < 1:
                    month += 12
                    year -= 1
                expected_month = (year, month)
                
                if log_month == expected_month:
                    streak += 1
                elif log_month < expected_month:
                    # Gap found, stop counting
                    break
        
        else:
            # For other frequencies, just count total logs
            streak = len(logs)
        
        habit.current_streak = streak
        
        # Update longest streak if needed
        if streak > habit.longest_streak:
            habit.longest_streak = streak
        
        self.db.commit()
        
        return streak, None
    
    def update_longest_streak(self, habit_id: UUID, user_id: UUID) -> Tuple[Optional[Habit], Optional[str]]:
        """
        Update longest streak if current streak is higher
        
        Args:
            habit_id: Habit UUID
            user_id: User UUID
            
        Returns:
            Tuple of (Habit, error_message)
        """
        habit = self.verify_habit_ownership(habit_id, user_id)
        
        if not habit:
            return None, "Habit not found or access denied"
        
        if habit.current_streak > habit.longest_streak:
            habit.longest_streak = habit.current_streak
            habit.updated_at = datetime.utcnow()
            self.db.commit()
            self.db.refresh(habit)
            logger.info(f"Longest streak updated: {habit_id} to {habit.longest_streak}")
        
        return habit, None
    
    def check_at_risk_habits(self, user_id: UUID, days_threshold: int = 3) -> List[Habit]:
        """
        Get habits at risk (3+ days missed for DAILY habits)
        
        Args:
            user_id: User UUID
            days_threshold: Number of days missed to consider at risk (default 3)
            
        Returns:
            List of at-risk habits
        """
        threshold_date = date.today() - timedelta(days=days_threshold)
        
        habits = self.db.query(Habit).filter(
            and_(
                Habit.user_id == user_id,
                Habit.frequency == HabitFrequency.DAILY,
                Habit.last_completed < threshold_date
            )
        ).all()
        
        # Also include habits that have never been completed
        never_completed = self.db.query(Habit).filter(
            and_(
                Habit.user_id == user_id,
                Habit.frequency == HabitFrequency.DAILY,
                Habit.last_completed.is_(None)
            )
        ).all()
        
        return habits + never_completed


def get_habit_service(db: Session) -> HabitService:
    """Factory function to create HabitService instance"""
    return HabitService(db)
