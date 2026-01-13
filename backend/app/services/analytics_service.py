"""
Analytics service with user_id filtering
"""

from datetime import date, timedelta
from typing import Dict, List, Optional, Any
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_, func, extract, Integer

from app.models.task import Task
from app.models.enums import TaskStatus
from app.models.category import Category
import logging

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Service for analytics operations with user filtering"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def calculate_completion_rate(self, total: int, completed: int) -> float:
        """
        Calculate completion rate percentage
        
        Args:
            total: Total number of tasks
            completed: Number of completed tasks
            
        Returns:
            Completion rate as percentage (0-100)
        """
        if total == 0:
            return 0.0
        return (completed / total) * 100
    
    def get_daily_analytics(self, user_id: UUID, target_date: date) -> Dict[str, Any]:
        """
        Get daily analytics for user
        
        Args:
            user_id: User UUID
            target_date: Date to analyze
            
        Returns:
            Dictionary with daily analytics
        """
        # Get all tasks for the day
        tasks = self.db.query(Task).filter(
            and_(
                Task.user_id == user_id,
                Task.scheduled_date == target_date
            )
        ).all()
        
        total_tasks = len(tasks)
        completed_tasks = sum(1 for t in tasks if t.status == TaskStatus.DONE)
        skipped_tasks = sum(1 for t in tasks if t.status == TaskStatus.SKIPPED)
        pending_tasks = sum(1 for t in tasks if t.status == TaskStatus.PENDING)
        
        completion_rate = self.calculate_completion_rate(total_tasks, completed_tasks)
        
        return {
            "date": target_date.isoformat(),
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "skipped_tasks": skipped_tasks,
            "pending_tasks": pending_tasks,
            "completion_rate": round(completion_rate, 2)
        }
    
    def get_weekly_analytics(self, user_id: UUID, end_date: Optional[date] = None) -> Dict[str, Any]:
        """
        Get weekly analytics for 7-day period ending on end_date
        
        Args:
            user_id: User UUID
            end_date: End date of week (default: today)
            
        Returns:
            Dictionary with weekly analytics
        """
        if end_date is None:
            end_date = date.today()
        
        start_date = end_date - timedelta(days=6)
        
        # Get all tasks for the week
        tasks = self.db.query(Task).filter(
            and_(
                Task.user_id == user_id,
                Task.scheduled_date >= start_date,
                Task.scheduled_date <= end_date
            )
        ).all()
        
        total_tasks = len(tasks)
        completed_tasks = sum(1 for t in tasks if t.status == TaskStatus.DONE)
        skipped_tasks = sum(1 for t in tasks if t.status == TaskStatus.SKIPPED)
        pending_tasks = sum(1 for t in tasks if t.status == TaskStatus.PENDING)
        
        completion_rate = self.calculate_completion_rate(total_tasks, completed_tasks)
        
        # Daily breakdown
        daily_data = []
        current_date = start_date
        while current_date <= end_date:
            daily_analytics = self.get_daily_analytics(user_id, current_date)
            daily_data.append(daily_analytics)
            current_date += timedelta(days=1)
        
        return {
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "skipped_tasks": skipped_tasks,
            "pending_tasks": pending_tasks,
            "completion_rate": round(completion_rate, 2),
            "daily_breakdown": daily_data
        }
    
    def get_monthly_analytics(self, user_id: UUID, year: int, month: int) -> Dict[str, Any]:
        """
        Get monthly analytics with category breakdown
        
        Args:
            user_id: User UUID
            year: Year
            month: Month (1-12)
            
        Returns:
            Dictionary with monthly analytics
        """
        # Get all tasks for the month
        tasks = self.db.query(Task).filter(
            and_(
                Task.user_id == user_id,
                extract('year', Task.scheduled_date) == year,
                extract('month', Task.scheduled_date) == month
            )
        ).all()
        
        total_tasks = len(tasks)
        completed_tasks = sum(1 for t in tasks if t.status == TaskStatus.DONE)
        skipped_tasks = sum(1 for t in tasks if t.status == TaskStatus.SKIPPED)
        pending_tasks = sum(1 for t in tasks if t.status == TaskStatus.PENDING)
        
        completion_rate = self.calculate_completion_rate(total_tasks, completed_tasks)
        
        # Category breakdown
        category_stats = self.aggregate_by_category(tasks)
        
        return {
            "year": year,
            "month": month,
            "total_tasks": total_tasks,
            "completed_tasks": completed_tasks,
            "skipped_tasks": skipped_tasks,
            "pending_tasks": pending_tasks,
            "completion_rate": round(completion_rate, 2),
            "category_breakdown": category_stats
        }
    
    def aggregate_by_category(self, tasks: List[Task]) -> List[Dict[str, Any]]:
        """
        Aggregate tasks by category with completion rates
        
        Args:
            tasks: List of tasks
            
        Returns:
            List of category statistics
        """
        category_map = {}
        
        for task in tasks:
            category_id = str(task.category_id) if task.category_id else "uncategorized"
            
            if category_id not in category_map:
                category_map[category_id] = {
                    "category_id": category_id,
                    "category_name": None,
                    "total": 0,
                    "completed": 0,
                    "skipped": 0,
                    "pending": 0
                }
            
            category_map[category_id]["total"] += 1
            
            if task.status == TaskStatus.DONE:
                category_map[category_id]["completed"] += 1
            elif task.status == TaskStatus.SKIPPED:
                category_map[category_id]["skipped"] += 1
            elif task.status == TaskStatus.PENDING:
                category_map[category_id]["pending"] += 1
        
        # Calculate percentages and fetch category names
        result = []
        for cat_id, stats in category_map.items():
            if cat_id != "uncategorized":
                category = self.db.query(Category).filter(Category.id == cat_id).first()
                stats["category_name"] = category.name if category else "Unknown"
            else:
                stats["category_name"] = "Uncategorized"
            
            stats["completion_rate"] = round(
                self.calculate_completion_rate(stats["total"], stats["completed"]), 2
            )
            result.append(stats)
        
        return result
    
    def get_task_insights(self, user_id: UUID, start_date: date, end_date: date) -> Dict[str, Any]:
        """
        Get task insights (most completed/skipped) for date range
        
        Args:
            user_id: User UUID
            start_date: Start date
            end_date: End date
            
        Returns:
            Dictionary with task insights
        """
        # Most completed tasks (by title)
        completed_tasks = self.db.query(
            Task.title,
            func.count(Task.id).label('count')
        ).filter(
            and_(
                Task.user_id == user_id,
                Task.scheduled_date >= start_date,
                Task.scheduled_date <= end_date,
                Task.status == TaskStatus.DONE
            )
        ).group_by(Task.title).order_by(func.count(Task.id).desc()).limit(5).all()
        
        # Most skipped tasks (by title)
        skipped_tasks = self.db.query(
            Task.title,
            func.count(Task.id).label('count')
        ).filter(
            and_(
                Task.user_id == user_id,
                Task.scheduled_date >= start_date,
                Task.scheduled_date <= end_date,
                Task.status == TaskStatus.SKIPPED
            )
        ).group_by(Task.title).order_by(func.count(Task.id).desc()).limit(5).all()
        
        return {
            "most_completed": [{"title": t[0], "count": t[1]} for t in completed_tasks],
            "most_skipped": [{"title": t[0], "count": t[1]} for t in skipped_tasks]
        }
    
    def generate_heatmap(self, user_id: UUID, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """
        Generate activity heatmap data for date range
        
        Args:
            user_id: User UUID
            start_date: Start date
            end_date: End date
            
        Returns:
            List of daily activity data
        """
        # Get task counts per day
        daily_counts = self.db.query(
            Task.scheduled_date,
            func.count(Task.id).label('total'),
            func.sum(func.cast(Task.status == TaskStatus.DONE, Integer)).label('completed')
        ).filter(
            and_(
                Task.user_id == user_id,
                Task.scheduled_date >= start_date,
                Task.scheduled_date <= end_date
            )
        ).group_by(Task.scheduled_date).all()
        
        # Create a map for quick lookup
        date_map = {
            row[0]: {"total": row[1], "completed": row[2] or 0}
            for row in daily_counts
        }
        
        # Generate data for all dates in range
        heatmap_data = []
        current_date = start_date
        while current_date <= end_date:
            data = date_map.get(current_date, {"total": 0, "completed": 0})
            heatmap_data.append({
                "date": current_date.isoformat(),
                "total_tasks": data["total"],
                "completed_tasks": data["completed"],
                "completion_rate": round(
                    self.calculate_completion_rate(data["total"], data["completed"]), 2
                )
            })
            current_date += timedelta(days=1)
        
        return heatmap_data


def get_analytics_service(db: Session) -> AnalyticsService:
    """Factory function to create AnalyticsService instance"""
    return AnalyticsService(db)
