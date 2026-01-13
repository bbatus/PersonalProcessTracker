from sqlalchemy import Column, String, Date, Time, Float, Integer, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class SleepLog(BaseModel):
    """Sleep log model for tracking sleep patterns"""
    __tablename__ = "sleep_logs"
    
    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Sleep data
    date = Column(Date, nullable=False, index=True)  # The date when sleep started
    sleep_time = Column(Time, nullable=False)  # Time when went to sleep (e.g., 23:30)
    wake_time = Column(Time, nullable=False)  # Time when woke up (e.g., 07:00)
    duration_hours = Column(Float, nullable=False)  # Calculated sleep duration in hours
    quality_score = Column(Integer, nullable=True)  # Sleep quality rating (1-10)
    notes = Column(Text, nullable=True)  # Optional notes about sleep
    
    # Relationships
    user = relationship("User", back_populates="sleep_logs")
    
    # Composite indexes for common queries
    __table_args__ = (
        Index('ix_sleep_logs_user_date', 'user_id', 'date'),
    )
    
    def __repr__(self):
        return f"<SleepLog(id={self.id}, date={self.date}, duration={self.duration_hours}h)>"
