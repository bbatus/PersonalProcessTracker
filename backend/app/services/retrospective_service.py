"""
Retrospective service with user_id validation
"""

from datetime import date
from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, extract, func
from sqlalchemy.exc import IntegrityError

from app.models.retrospective import MonthlySummary, MoodLog
from app.models.task import Task
from app.models.enums import TaskStatus
import logging

logger = logging.getLogger(__name__)


class RetrospectiveService:
    """Service for retrospective operations with user authorization"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_or_update_retrospective(
        self,
        user_id: UUID,
        month: date,
        what_went_well: str,
        what_went_bad: str,
        what_to_change: str,
        average_mood: Optional[float] = None
    ) -> Tuple[Optional[MonthlySummary], Optional[str]]:
        """
        Create or update retrospective (upsert logic)
        
        Args:
            user_id: User UUID
            month: Month date (YYYY-MM-01 format)
            what_went_well: What went well text
            what_went_bad: What went bad text
            what_to_change: What to change text
            average_mood: Optional average mood score (1-10)
            
        Returns:
            Tuple of (MonthlySummary, error_message)
        """
        # Validate mood score
        if average_mood is not None and (average_mood < 1 or average_mood > 10):
            return None, "Mood score must be between 1 and 10"
        
        # Normalize month to first day
        month_normalized = date(month.year, month.month, 1)
        
        # Check if retrospective exists
        existing = self.db.query(MonthlySummary).filter(
            and_(
                MonthlySummary.user_id == user_id,
                MonthlySummary.month == month_normalized
            )
        ).first()
        
        if existing:
            # Update existing
            existing.what_went_well = what_went_well
            existing.what_went_bad = what_went_bad
            existing.what_to_change = what_to_change
            if average_mood is not None:
                existing.average_mood = average_mood
            
            # Recalculate stats
            stats = self.calculate_monthly_stats(user_id, month_normalized)
            existing.success_rate = stats.get("success_rate")
            existing.total_tasks = stats.get("total_tasks")
            existing.completed_tasks = stats.get("completed_tasks")
            
            self.db.commit()
            self.db.refresh(existing)
            
            logger.info(f"Retrospective updated: {existing.id} for user {user_id}")
            return existing, None
        else:
            # Create new
            stats = self.calculate_monthly_stats(user_id, month_normalized)
            
            retrospective = MonthlySummary(
                user_id=user_id,
                month=month_normalized,
                what_went_well=what_went_well,
                what_went_bad=what_went_bad,
                what_to_change=what_to_change,
                average_mood=average_mood,
                success_rate=stats.get("success_rate"),
                total_tasks=stats.get("total_tasks"),
                completed_tasks=stats.get("completed_tasks")
            )
            
            self.db.add(retrospective)
            self.db.commit()
            self.db.refresh(retrospective)
            
            logger.info(f"Retrospective created: {retrospective.id} for user {user_id}")
            return retrospective, None
    
    def get_retrospective(self, user_id: UUID, month: date) -> Optional[MonthlySummary]:
        """
        Get retrospective by month
        
        Args:
            user_id: User UUID
            month: Month date
            
        Returns:
            MonthlySummary if found, None otherwise
        """
        # Normalize month to first day
        month_normalized = date(month.year, month.month, 1)
        
        retrospective = self.db.query(MonthlySummary).filter(
            and_(
                MonthlySummary.user_id == user_id,
                MonthlySummary.month == month_normalized
            )
        ).first()
        
        return retrospective
    
    def get_retrospectives(
        self,
        user_id: UUID,
        skip: int = 0,
        limit: int = 12
    ) -> List[MonthlySummary]:
        """
        Get all retrospectives for user
        
        Args:
            user_id: User UUID
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return
            
        Returns:
            List of retrospectives ordered by month descending
        """
        retrospectives = self.db.query(MonthlySummary).filter(
            MonthlySummary.user_id == user_id
        ).order_by(MonthlySummary.month.desc()).offset(skip).limit(limit).all()
        
        return retrospectives
    
    def calculate_monthly_stats(self, user_id: UUID, month: date) -> Dict[str, Any]:
        """
        Calculate automatic monthly statistics
        
        Args:
            user_id: User UUID
            month: Month date
            
        Returns:
            Dictionary with monthly statistics
        """
        # Get all tasks for the month
        tasks = self.db.query(Task).filter(
            and_(
                Task.user_id == user_id,
                extract('year', Task.scheduled_date) == month.year,
                extract('month', Task.scheduled_date) == month.month
            )
        ).all()
        
        total_tasks = len(tasks)
        completed_tasks = sum(1 for t in tasks if t.status == TaskStatus.DONE)
        
        success_rate = 0.0
        if total_tasks > 0:
            success_rate = (completed_tasks / total_tasks) * 100
        
        return {
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "success_rate": round(success_rate, 2)
        }
    
    def log_mood(
        self,
        user_id: UUID,
        log_date: date,
        mood_score: int,
        notes: Optional[str] = None
    ) -> Tuple[Optional[MoodLog], Optional[str]]:
        """
        Log daily mood
        
        Args:
            user_id: User UUID
            log_date: Date of mood log
            mood_score: Mood score (1-10)
            notes: Optional notes
            
        Returns:
            Tuple of (MoodLog, error_message)
        """
        # Validate mood score
        if mood_score < 1 or mood_score > 10:
            return None, "Mood score must be between 1 and 10"
        
        # Check if mood log exists for this date
        existing = self.db.query(MoodLog).filter(
            and_(
                MoodLog.user_id == user_id,
                MoodLog.date == log_date
            )
        ).first()
        
        if existing:
            # Update existing
            existing.mood_score = mood_score
            existing.notes = notes
            self.db.commit()
            self.db.refresh(existing)
            logger.info(f"Mood log updated: {existing.id} for user {user_id}")
            return existing, None
        else:
            # Create new
            mood_log = MoodLog(
                user_id=user_id,
                date=log_date,
                mood_score=mood_score,
                notes=notes
            )
            
            try:
                self.db.add(mood_log)
                self.db.commit()
                self.db.refresh(mood_log)
                logger.info(f"Mood log created: {mood_log.id} for user {user_id}")
                return mood_log, None
            except IntegrityError:
                self.db.rollback()
                return None, "Mood log already exists for this date"
    
    def get_mood_logs(
        self,
        user_id: UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[MoodLog]:
        """
        Get mood logs for user with optional date range
        
        Args:
            user_id: User UUID
            start_date: Optional start date
            end_date: Optional end date
            
        Returns:
            List of mood logs
        """
        query = self.db.query(MoodLog).filter(MoodLog.user_id == user_id)
        
        if start_date:
            query = query.filter(MoodLog.date >= start_date)
        if end_date:
            query = query.filter(MoodLog.date <= end_date)
        
        mood_logs = query.order_by(MoodLog.date.desc()).all()
        
        return mood_logs


def get_retrospective_service(db: Session) -> RetrospectiveService:
    """Factory function to create RetrospectiveService instance"""
    return RetrospectiveService(db)
