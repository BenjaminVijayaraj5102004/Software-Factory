from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from backend.app.models.todo import Todo


class SubtaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    is_completed: bool = Field(default=False, index=True)
    todo_id: int = Field(foreign_key="todo.id", index=True)


class Subtask(SubtaskBase, table=True):
    __tablename__ = "subtask"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    todo: Optional["Todo"] = Relationship(back_populates="subtasks")
