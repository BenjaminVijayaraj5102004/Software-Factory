from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from backend.app.models.todo import Todo


class CategoryBase(SQLModel):
    name: str = Field(index=True, unique=True, min_length=1, max_length=100)
    color: str = Field(default="#6366f1", max_length=50)
    icon: Optional[str] = Field(default="folder", max_length=50)


class Category(CategoryBase, table=True):
    __tablename__ = "category"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    todos: List["Todo"] = Relationship(back_populates="category")
