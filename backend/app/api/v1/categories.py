from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from backend.app.core.database import get_session
from backend.app.models.category import Category
from backend.app.schemas.category import CategoryCreate, CategoryRead

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=List[CategoryRead], status_code=status.HTTP_200_OK)
def list_categories(session: Session = Depends(get_session)):
    """List all categories."""
    statement = select(Category).order_by(Category.name)
    categories = session.exec(statement).all()
    return categories


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
def create_category(category_in: CategoryCreate, session: Session = Depends(get_session)):
    """Create a new category."""
    existing = session.exec(select(Category).where(Category.name == category_in.name)).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Category '{category_in.name}' already exists",
        )
    category = Category(name=category_in.name, color=category_in.color)
    session.add(category)
    session.commit()
    session.refresh(category)
    return category
