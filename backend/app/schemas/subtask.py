from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class SubtaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=255, description="Subtask title")
    is_completed: bool = Field(default=False, description="Completion status")


class SubtaskUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=1, max_length=255)
    is_completed: Optional[bool] = Field(default=None)


class SubtaskRead(BaseModel):
    id: int
    todo_id: int
    title: str
    is_completed: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
