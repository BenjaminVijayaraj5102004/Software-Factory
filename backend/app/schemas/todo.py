from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field
from backend.app.models.enums import Priority, Status
from backend.app.schemas.category import CategoryRead


class TodoBaseSchema(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Title of the todo item")
    description: Optional[str] = Field(default=None, description="Detailed description or notes")
    priority: Priority = Field(default=Priority.MEDIUM, description="Priority level")
    status: Status = Field(default=Status.PENDING, description="Current workflow status")
    due_date: Optional[datetime] = Field(default=None, description="Optional due date timestamp")
    tags: Optional[str] = Field(default=None, description="Comma-separated tags (e.g. 'work,urgent')")
    category_id: Optional[int] = Field(default=None, description="Foreign key to category")


class TodoCreate(TodoBaseSchema):
    category_name: Optional[str] = Field(
        default=None,
        description="Optional category name to automatically find or create and associate"
    )


class TodoUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = Field(default=None)
    priority: Optional[Priority] = Field(default=None)
    status: Optional[Status] = Field(default=None)
    due_date: Optional[datetime] = Field(default=None)
    tags: Optional[str] = Field(default=None)
    category_id: Optional[int] = Field(default=None)


class TodoRead(TodoBaseSchema):
    id: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    category: Optional[CategoryRead] = None
    subtasks_count: int = 0
    subtasks_completed_count: int = 0
    progress_percentage: float = 0.0
    is_overdue: bool = False

    model_config = ConfigDict(from_attributes=True)


class TodoListResponse(BaseModel):
    items: List[TodoRead]
    total: int
    page: int
    limit: int
    total_pages: int
