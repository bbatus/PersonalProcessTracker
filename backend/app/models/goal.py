from sqlalchemy import Column, String, Text, Integer, Date, ForeignKey, Index, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.models.base import BaseModel
from app.models.enums import GoalPeriod


class Goal(BaseModel):
    """Goal model with user_id for data isolation"""
    __tablename__ = "goals"
    
    # Foreign keys
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True)
    
    # Goal data
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    period = Column(SQLEnum(GoalPeriod), nullable=False, index=True)
    target_count = Column(Integer, nullable=False)
    current_count = Column(Integer, default=0, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False, index=True)
    
    # Relationships
    user = relationship("User", back_populates="goals")
    category = relationship("Category", back_populates="goals")
    tasks = relationship("Task", back_populates="goal")
    
    # Composite indexes for common queries
    __table_args__ = (
        Index('ix_goals_user_period', 'user_id', 'period'),
        Index('ix_goals_user_end_date', 'user_id', 'end_date'),
    )
    
    def __repr__(self):
        return f"<Goal(id={self.id}, title={self.title}, progress={self.current_count}/{self.target_count})>"
