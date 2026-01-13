from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.models.base import BaseModel


class Category(BaseModel):
    """Category model for tasks and goals"""
    __tablename__ = "categories"
    
    name = Column(String(50), nullable=False, unique=True)
    color = Column(String(7), nullable=False)  # Hex color code
    
    # Relationships
    tasks = relationship("Task", back_populates="category")
    goals = relationship("Goal", back_populates="category")
    
    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name})>"


# Default categories seed data
DEFAULT_CATEGORIES = [
    {"name": "Work", "color": "#3B82F6"},      # Blue
    {"name": "Sport", "color": "#10B981"},     # Green
    {"name": "Personal", "color": "#F59E0B"},  # Amber
    {"name": "Learning", "color": "#8B5CF6"},  # Purple
]
