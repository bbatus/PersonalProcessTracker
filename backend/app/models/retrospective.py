from sqlalchemy import Column, Date, Integer, Float, Text, ForeignKey, UniqueConstraint, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class MonthlySummary(BaseModel):
    """Monthly retrospective summary with user_id for data isolation"""
    __tablename__ = "monthly_summaries"
    
    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Summary data
    month = Column(Date, nullable=False)  # YYYY-MM-01 format
    success_rate = Column(Float, nullable=True)
    total_tasks = Column(Integer, nullable=True)
    completed_tasks = Column(Integer, nullable=True)
    
    # Retrospective text
    what_went_well = Column(Text, nullable=False)
    what_went_bad = Column(Text, nullable=False)
    what_to_change = Column(Text, nullable=False)
    
    # Mood tracking
    average_mood = Column(Float, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="monthly_summaries")
    
    # Unique constraint to prevent duplicate summaries
    __table_args__ = (
        UniqueConstraint('user_id', 'month', name='uq_user_month'),
        CheckConstraint('average_mood >= 1 AND average_mood <= 10', name='ck_average_mood_range'),
    )
    
    def __repr__(self):
        return f"<MonthlySummary(id={self.id}, user_id={self.user_id}, month={self.month})>"


class MoodLog(BaseModel):
    """Daily mood log with user_id for data isolation"""
    __tablename__ = "mood_logs"
    
    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Mood data
    date = Column(Date, nullable=False, index=True)
    mood_score = Column(Integer, nullable=False)
    notes = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="mood_logs")
    
    # Unique constraint and check constraint
    __table_args__ = (
        UniqueConstraint('user_id', 'date', name='uq_user_mood_date'),
        CheckConstraint('mood_score >= 1 AND mood_score <= 10', name='ck_mood_score_range'),
    )
    
    def __repr__(self):
        return f"<MoodLog(id={self.id}, user_id={self.user_id}, date={self.date}, score={self.mood_score})>"
