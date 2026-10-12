from datetime import datetime, timezone
from typing import TYPE_CHECKING, List, Optional
from sqlmodel import Field, Relationship, SQLModel
from backend.app.models.enums import Priority, Status

if TYPE_CHECKING:
    from backend.app.models.category import Category
    from backend.app.models.subtask import Subtask


class TodoBase(SQLModel):
    title: str = Field(index=True, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None)
    priority: Priority = Field(default=Priority.MEDIUM, index=True)
    status: Status = Field(default=Status.PENDING, index=True)
    due_date: Optional[datetime] = Field(default=None, index=True)
    tags: Optional[str] = Field(default=None, index=True)
    category_id: Optional[int] = Field(default=None, foreign_key="category.id", index=True)


class Todo(TodoBase, table=True):
    __tablename__ = "todo"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = Field(default=None, index=True)

    category: Optional["Category"] = Relationship(back_populates="todos")
    subtasks: List["Subtask"] = Relationship(back_populates="todo", cascade_delete=True)
