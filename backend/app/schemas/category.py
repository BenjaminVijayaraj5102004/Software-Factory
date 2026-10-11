from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class CategoryBaseSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    color: str = Field(default="#6366f1", max_length=50)
    icon: Optional[str] = Field(default="folder", max_length=50)


class CategoryCreate(CategoryBaseSchema):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    color: Optional[str] = Field(default=None, max_length=50)
    icon: Optional[str] = Field(default=None, max_length=50)


class CategoryRead(CategoryBaseSchema):
    id: int
    created_at: datetime
    todos_count: int = 0

    model_config = ConfigDict(from_attributes=True)
