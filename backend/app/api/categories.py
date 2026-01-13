"""
Category API endpoints (public)
"""

from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.category import Category

router = APIRouter(prefix="/api/categories", tags=["categories"])


# Pydantic schemas
class CategoryResponse(BaseModel):
    id: UUID
    name: str
    color: str

    class Config:
        from_attributes = True


@router.get("", response_model=List[CategoryResponse])
def list_categories(db: Session = Depends(get_db)):
    """List all categories (public endpoint)"""
    categories = db.query(Category).all()
    return categories
