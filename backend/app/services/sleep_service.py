"""
Sleep service with user_id validation and authorization
"""

from datetime import datetime, date, time, timedelta
from typing import List, Optional, Tuple, Dict
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, func

from app.models.sleep import SleepLog
import logging

logger = logging.getLogger(__name__)


class SleepService:
    """Service for sleep log CRUD operations with user authorization"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def verify_sleep_log_ownership(self, sleep_log_id: UUID, user_id: UUID) -> Optional[SleepLog]:
        """
        Verify that a sleep log belongs to the user
        
        Args:
            sleep_log_id: SleepLog UUID
            user_id: User UUID
            
        Returns:
            SleepLog if found and owned by user, None otherwise
        """
        sleep_log = self.db.query(SleepLog).filter(
            and_(SleepLog.id == sleep_log_id, SleepLog.user_id == user_id)
        ).first()
        
        return sleep_log
    
    def calculate_duration(self, sleep_time: time, wake_time: time) -> float:
        """
        Calculate sleep duration in hours
        
        Args:
            sleep_time: Time when went to sleep
            wake_time: Time when woke up
            
        Returns:
            Duration in hours (handles overnight sleep)
        """
        # Create datetime objects for calculation
        today = date.today()
        sleep_dt = datetime.combine(today, sleep_time)
        wake_dt = datetime.combine(today, wake_time)
        
        # If wake time is earlier than sleep time, it means next day
        if wake_dt <= sleep_dt:
            wake_dt += timedelta(days=1)
        
        duration = (wake_dt - sleep_dt).total_seconds() / 3600  # Convert to hours
        return round(duration, 2)
    
    def create_sleep_log(
        self,
        user_id: UUID,
        date: date,
        sleep_time: time,
        wake_time: time,
        quality_score: Optional[int] = None,
        notes: Optional[str] = None
    ) -> SleepLog:
        """
        Create a new sleep log for user
        
        Args:
            user_id: User UUID
            date: Date when sleep started
            sleep_time: Time when went to sleep
            wake_time: Time when woke up
            quality_score: Sleep quality rating (1-10)
            notes: Optional notes
            
        Returns:
            Created sleep log
        """
        # Calculate duration
        duration_hours = self.calculate_duration(sleep_time, wake_time)
        
        sleep_log = SleepLog(
            user_id=user_id,
            date=date,
            sleep_time=sleep_time,
            wake_time=wake_time,
            duration_hours=duration_hours,
            quality_score=quality_score,
            notes=notes
        )
        
        self.db.add(sleep_log)
        self.db.commit()
        self.db.refresh(sleep_log)
        
        logger.info(f"Sleep log created: {sleep_log.id} for user {user_id}")
        return sleep_log
    
    def get_sleep_logs(
        self,
        user_id: UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[SleepLog]:
        """
        Get sleep logs for user with optional date filtering
        
        Args:
            user_id: User UUID
            start_date: Optional start date filter
            end_date: Optional end date filter
            skip: Number of records to skip (pagination)
            limit: Maximum number of records to return
            
        Returns:
            List of sleep logs
        """
        query = self.db.query(SleepLog).filter(SleepLog.user_id == user_id)
        
        if start_date:
            query = query.filter(SleepLog.date >= start_date)
        if end_date:
            query = query.filter(SleepLog.date <= end_date)
        
        # Order by date descending (most recent first)
        query = query.order_by(SleepLog.date.desc())
        
        sleep_logs = query.offset(skip).limit(limit).all()
        
        return sleep_logs
    
    def get_sleep_log(self, sleep_log_id: UUID, user_id: UUID) -> Optional[SleepLog]:
        """
        Get a single sleep log with ownership verification
        
        Args:
            sleep_log_id: SleepLog UUID
            user_id: User UUID
            
        Returns:
            SleepLog if found and owned by user, None otherwise
        """
        return self.verify_sleep_log_ownership(sleep_log_id, user_id)
    
    def update_sleep_log(
        self,
        sleep_log_id: UUID,
        user_id: UUID,
        date: Optional[date] = None,
        sleep_time: Optional[time] = None,
        wake_time: Optional[time] = None,
        quality_score: Optional[int] = None,
        notes: Optional[str] = None
    ) -> Tuple[Optional[SleepLog], Optional[str]]:
        """
        Update a sleep log with ownership verification
        
        Args:
            sleep_log_id: SleepLog UUID
            user_id: User UUID
            date: Optional new date
            sleep_time: Optional new sleep time
            wake_time: Optional new wake time
            quality_score: Optional new quality score
            notes: Optional new notes
            
        Returns:
            Tuple of (SleepLog, error_message). SleepLog is None if update failed.
        """
        sleep_log = self.verify_sleep_log_ownership(sleep_log_id, user_id)
        
        if not sleep_log:
            return None, "Sleep log not found or access denied"
        
        # Update fields if provided
        if date is not None:
            sleep_log.date = date
        if sleep_time is not None:
            sleep_log.sleep_time = sleep_time
        if wake_time is not None:
            sleep_log.wake_time = wake_time
        if quality_score is not None:
            sleep_log.quality_score = quality_score
        if notes is not None:
            sleep_log.notes = notes
        
        # Recalculate duration if times changed
        if sleep_time is not None or wake_time is not None:
            sleep_log.duration_hours = self.calculate_duration(
                sleep_log.sleep_time, 
                sleep_log.wake_time
            )
        
        # Update timestamp
        sleep_log.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(sleep_log)
        
        logger.info(f"Sleep log updated: {sleep_log.id}")
        return sleep_log, None
    
    def delete_sleep_log(self, sleep_log_id: UUID, user_id: UUID) -> Tuple[bool, Optional[str]]:
        """
        Delete a sleep log with ownership verification
        
        Args:
            sleep_log_id: SleepLog UUID
            user_id: User UUID
            
        Returns:
            Tuple of (success, error_message)
        """
        sleep_log = self.verify_sleep_log_ownership(sleep_log_id, user_id)
        
        if not sleep_log:
            return False, "Sleep log not found or access denied"
        
        self.db.delete(sleep_log)
        self.db.commit()
        
        logger.info(f"Sleep log deleted: {sleep_log_id}")
        return True, None
    
    def get_sleep_statistics(
        self,
        user_id: UUID,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict:
        """
        Get sleep statistics for a date range
        
        Args:
            user_id: User UUID
            start_date: Optional start date
            end_date: Optional end date
            
        Returns:
            Dictionary with sleep statistics
        """
        query = self.db.query(SleepLog).filter(SleepLog.user_id == user_id)
        
        if start_date:
            query = query.filter(SleepLog.date >= start_date)
        if end_date:
            query = query.filter(SleepLog.date <= end_date)
        
        logs = query.all()
        
        if not logs:
            return {
                "total_logs": 0,
                "average_duration": 0,
                "average_quality": 0,
                "total_sleep_hours": 0,
                "best_sleep": None,
                "worst_sleep": None
            }
        
        durations = [log.duration_hours for log in logs]
        qualities = [log.quality_score for log in logs if log.quality_score is not None]
        
        # Find best and worst sleep
        best_sleep = max(logs, key=lambda x: x.duration_hours)
        worst_sleep = min(logs, key=lambda x: x.duration_hours)
        
        return {
            "total_logs": len(logs),
            "average_duration": round(sum(durations) / len(durations), 2),
            "average_quality": round(sum(qualities) / len(qualities), 2) if qualities else None,
            "total_sleep_hours": round(sum(durations), 2),
            "best_sleep": {
                "date": best_sleep.date.isoformat(),
                "duration": best_sleep.duration_hours
            },
            "worst_sleep": {
                "date": worst_sleep.date.isoformat(),
                "duration": worst_sleep.duration_hours
            }
        }


def get_sleep_service(db: Session) -> SleepService:
    """Factory function to create SleepService instance"""
    return SleepService(db)
