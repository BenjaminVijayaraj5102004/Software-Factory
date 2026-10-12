import math
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session

from backend.app.core.database import get_session
from backend.app.models.enums import Priority, Status
from backend.app.schemas.category import CategoryCreate, CategoryRead
from backend.app.schemas.subtask import SubtaskCreate, SubtaskRead
from backend.app.schemas.todo import TodoCreate, TodoListResponse, TodoRead, TodoUpdate
from backend.app.services.category_service import CategoryService
from backend.app.services.subtask_service import SubtaskService
from backend.app.services.todo_service import TodoService

router = APIRouter()


@router.get("", response_model=TodoListResponse, summary="List todos with filters and pagination")
def list_todos(
    status: Optional[Status] = Query(default=None, description="Filter by status"),
    priority: Optional[Priority] = Query(default=None, description="Filter by priority"),
    category_id: Optional[int] = Query(default=None, description="Filter by category ID"),
    category: Optional[str] = Query(default=None, description="Filter by category name"),
    search: Optional[str] = Query(default=None, description="Search across title, description, and tags"),
    is_completed: Optional[bool] = Query(default=None, description="Filter by boolean completion state"),
    page: int = Query(default=1, ge=1, description="Page number starting at 1"),
    limit: int = Query(default=50, ge=1, le=100, description="Items per page"),
    sort_by: str = Query(
        default="created_at_desc",
        description="Sort by: created_at_desc, created_at_asc, due_date_asc, due_date_desc, priority_desc",
    ),
    session: Session = Depends(get_session),
):
    """Retrieve paginated todos with optional filtering and sorting."""
    items, total = TodoService.list_todos(
        session=session,
        status=status,
        priority=priority,
        category_id=category_id,
        category=category,
        search=search,
        is_completed=is_completed,
        page=page,
        limit=limit,
        sort_by=sort_by,
    )
    total_pages = math.ceil(total / limit) if total > 0 else 1
    return TodoListResponse(
        items=items,
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages,
    )


@router.post("", response_model=TodoRead, status_code=status.HTTP_201_CREATED, summary="Create a new todo")
def create_todo(
    todo_in: TodoCreate,
    session: Session = Depends(get_session),
):
    """Create a new todo item."""
    return TodoService.create_todo(session=session, todo_in=todo_in)


@router.get("/categories", response_model=List[CategoryRead], summary="List all categories")
def list_categories(
    session: Session = Depends(get_session),
):
    """List all categories available for task tagging."""
    categories = CategoryService.list_categories(session=session)
    return [
        CategoryRead(
            id=cat.id,
            name=cat.name,
            color=cat.color,
            icon=cat.icon,
            created_at=cat.created_at,
            todos_count=len(cat.todos) if hasattr(cat, "todos") and cat.todos else 0,
        )
        for cat in categories
    ]


@router.post(
    "/categories",
    response_model=CategoryRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a category",
)
def create_category(
    category_in: CategoryCreate,
    session: Session = Depends(get_session),
):
    """Create a new category tag."""
    cat = CategoryService.create(session=session, category_in=category_in)
    return CategoryRead(
        id=cat.id,
        name=cat.name,
        color=cat.color,
        icon=cat.icon,
        created_at=cat.created_at,
        todos_count=0,
    )


@router.get("/{todo_id}", response_model=TodoRead, summary="Get todo details by ID")
def get_todo(
    todo_id: int,
    session: Session = Depends(get_session),
):
    """Retrieve detailed information for a single todo."""
    todo = TodoService.get_todo(session=session, todo_id=todo_id)
    if not todo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with ID {todo_id} not found",
        )
    return todo


@router.put("/{todo_id}", response_model=TodoRead, summary="Update an existing todo")
def update_todo(
    todo_id: int,
    todo_in: TodoUpdate,
    session: Session = Depends(get_session),
):
    """Update fields on an existing todo item."""
    updated = TodoService.update_todo(session=session, todo_id=todo_id, todo_in=todo_in)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with ID {todo_id} not found",
        )
    return updated


@router.patch("/{todo_id}", response_model=TodoRead, summary="Partially update an existing todo")
def patch_todo(
    todo_id: int,
    todo_in: TodoUpdate,
    session: Session = Depends(get_session),
):
    """Partially update fields on an existing todo item."""
    updated = TodoService.update_todo(session=session, todo_id=todo_id, todo_in=todo_in)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with ID {todo_id} not found",
        )
    return updated


@router.delete("/{todo_id}", status_code=status.HTTP_200_OK, summary="Delete a todo")
def delete_todo(
    todo_id: int,
    session: Session = Depends(get_session),
):
    """Delete a todo item permanently."""
    success = TodoService.delete_todo(session=session, todo_id=todo_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with ID {todo_id} not found",
        )
    return {"message": "Todo deleted successfully", "id": todo_id}


@router.patch("/{todo_id}/toggle", response_model=TodoRead, summary="Toggle completion status")
def toggle_todo(
    todo_id: int,
    session: Session = Depends(get_session),
):
    """Toggle between COMPLETED and PENDING status."""
    toggled = TodoService.toggle_todo(session=session, todo_id=todo_id)
    if not toggled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with ID {todo_id} not found",
        )
    return toggled


@router.get("/{todo_id}/subtasks", response_model=List[SubtaskRead], summary="Get subtasks of a todo")
def get_todo_subtasks(
    todo_id: int,
    session: Session = Depends(get_session),
):
    """Retrieve all subtasks associated with a todo checklist."""
    return SubtaskService.get_subtasks_for_todo(session=session, todo_id=todo_id)


@router.post(
    "/{todo_id}/subtasks",
    response_model=SubtaskRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add a subtask to a todo",
)
def create_todo_subtask(
    todo_id: int,
    subtask_in: SubtaskCreate,
    session: Session = Depends(get_session),
):
    """Add a subtask to a todo checklist."""
    return SubtaskService.create_subtask(session=session, todo_id=todo_id, subtask_in=subtask_in)
