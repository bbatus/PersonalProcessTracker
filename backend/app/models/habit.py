from sqlalchemy import Column, String, Integer, Date, ForeignKey, Index, Enum as SQLEnum, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.models.enums import HabitFrequency


class Habit(BaseModel):
    """Habit model with user_id for data isolation"""
    __tablename__ = "habits"
    
    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Habit data
    name = Column(String(100), nullable=False)
    frequency = Column(SQLEnum(HabitFrequency), nullable=False)
    target_days = Column(Integer, nullable=True)  # For WEEKLY habits
    duration_days = Column(Integer, nullable=True)  # How many days this habit should last
    start_date = Column(Date, nullable=True)  # When the habit started
    current_streak = Column(Integer, default=0, nullable=False)
    longest_streak = Column(Integer, default=0, nullable=False)
    last_completed = Column(Date, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="habits")
    logs = relationship("HabitLog", back_populates="habit", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="habit", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Habit(id={self.id}, name={self.name}, streak={self.current_streak})>"


class HabitLog(BaseModel):
    """Habit log model for tracking completions"""
    __tablename__ = "habit_logs"
    
    # Foreign keys
    habit_id = Column(UUID(as_uuid=True), ForeignKey("habits.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Log data
    completed_date = Column(Date, nullable=False, index=True)
    notes = Column(Text, nullable=True)
    
    # Relationships
    habit = relationship("Habit", back_populates="logs")
    
    # Unique constraint to prevent duplicate logs
    __table_args__ = (
        UniqueConstraint('habit_id', 'completed_date', name='uq_habit_log_date'),
    )
    
    def __repr__(self):
        return f"<HabitLog(id={self.id}, habit_id={self.habit_id}, date={self.completed_date})>"
