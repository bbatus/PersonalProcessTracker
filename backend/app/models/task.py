from sqlalchemy import Column, String, Text, Date, DateTime, Integer, ForeignKey, Index, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.models.enums import TaskStatus


class Task(BaseModel):
    """Task model with user_id for data isolation"""
    __tablename__ = "tasks"
    
    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True, index=True)
    habit_id = Column(UUID(as_uuid=True), ForeignKey("habits.id", ondelete="CASCADE"), nullable=True, index=True)
    goal_id = Column(UUID(as_uuid=True), ForeignKey("goals.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Task data
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)  # User notes/feedback after completion
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING, nullable=False, index=True)
    scheduled_date = Column(Date, nullable=False, index=True)
    completed_at = Column(DateTime, nullable=True)
    estimated_duration = Column(Integer, nullable=True)  # Duration in minutes
    
    # Relationships
    user = relationship("User", back_populates="tasks")
    category = relationship("Category", back_populates="tasks")
    habit = relationship("Habit", back_populates="tasks")
    goal = relationship("Goal", back_populates="tasks")
    
    # Composite indexes for common queries
    __table_args__ = (
        Index('ix_tasks_user_date', 'user_id', 'scheduled_date'),
        Index('ix_tasks_user_status', 'user_id', 'status'),
        Index('ix_tasks_user_category', 'user_id', 'category_id'),
        Index('ix_tasks_user_goal', 'user_id', 'goal_id'),
    )
    
    def __repr__(self):
        return f"<Task(id={self.id}, title={self.title}, status={self.status})>"
