from typing import Dict, List
from pydantic import BaseModel, Field


class CategoryBreakdown(BaseModel):
    category_id: int
    name: str
    count: int
    color: str


class AnalyticsStats(BaseModel):
    total_todos: int = Field(default=0, description="Total number of todos")
    completed_todos: int = Field(default=0, description="Number of completed todos")
    pending_todos: int = Field(default=0, description="Number of pending todos")
    in_progress_todos: int = Field(default=0, description="Number of in-progress todos")
    overdue_todos: int = Field(default=0, description="Number of overdue todos")
    completion_rate: float = Field(default=0.0, description="Percentage of completed todos")
    priority_breakdown: Dict[str, int] = Field(
        default_factory=dict, description="Count of todos grouped by priority"
    )
    category_breakdown: List[CategoryBreakdown] = Field(
        default_factory=list, description="Count of todos grouped by category"
    )
    subtasks_total: int = Field(default=0, description="Total number of subtasks")
    subtasks_completed: int = Field(default=0, description="Completed subtasks count")
    subtask_completion_rate: float = Field(default=0.0, description="Subtask completion percentage")
