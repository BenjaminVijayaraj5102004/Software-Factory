from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session

from backend.app.core.database import get_session
from backend.app.schemas.subtask import SubtaskCreate, SubtaskRead, SubtaskUpdate
from backend.app.modules.subtasks.subtask_service import SubtaskService

router = APIRouter()


@router.get("/todos/{todo_id}/subtasks", response_model=List[SubtaskRead], summary="List subtasks for a todo")
@router.get("/{todo_id}/subtasks", response_model=List[SubtaskRead], summary="List subtasks for a todo (direct)")
def list_subtasks(
    todo_id: int,
    session: Session = Depends(get_session),
):
    """Retrieve checklist subtasks for a todo."""
    return SubtaskService.list_subtasks(session=session, todo_id=todo_id)


@router.post(
    "/todos/{todo_id}/subtasks",
    response_model=SubtaskRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add a subtask to a todo",
)
@router.post(
    "/{todo_id}/subtasks",
    response_model=SubtaskRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add a subtask to a todo (direct)",
)
def create_subtask(
    todo_id: int,
    subtask_in: SubtaskCreate,
    session: Session = Depends(get_session),
):
    """Create a subtask item attached to a parent todo."""
    created = SubtaskService.create_subtask(session=session, todo_id=todo_id, subtask_in=subtask_in)
    if not created:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Todo with ID {todo_id} not found",
        )
    return created


@router.patch("/todos/{todo_id}/subtasks/{subtask_id}", response_model=SubtaskRead, summary="Update subtask under todo")
@router.patch("/subtasks/{subtask_id}", response_model=SubtaskRead, summary="Update subtask directly")
def update_subtask(
    subtask_id: int,
    subtask_in: SubtaskUpdate,
    todo_id: int = None,
    session: Session = Depends(get_session),
):
    """Update a subtask (e.g. toggle completion or edit title)."""
    updated = SubtaskService.update_subtask(session=session, subtask_id=subtask_id, subtask_in=subtask_in)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subtask with ID {subtask_id} not found",
        )
    return updated


@router.delete("/todos/{todo_id}/subtasks/{subtask_id}", status_code=status.HTTP_200_OK, summary="Delete subtask under todo")
@router.delete("/subtasks/{subtask_id}", status_code=status.HTTP_200_OK, summary="Delete subtask directly")
def delete_subtask(
    subtask_id: int,
    todo_id: int = None,
    session: Session = Depends(get_session),
):
    """Delete a subtask permanently."""
    success = SubtaskService.delete_subtask(session=session, subtask_id=subtask_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subtask with ID {subtask_id} not found",
        )
    return {"message": "Subtask deleted successfully", "id": subtask_id}


@router.patch("/todos/{todo_id}/subtasks/{subtask_id}/toggle", response_model=SubtaskRead, summary="Toggle subtask completion")
@router.patch("/subtasks/{subtask_id}/toggle", response_model=SubtaskRead, summary="Toggle subtask completion directly")
def toggle_subtask(
    subtask_id: int,
    todo_id: int = None,
    session: Session = Depends(get_session),
):
    """Toggle a subtask completion status."""
    toggled = SubtaskService.toggle_subtask(session=session, subtask_id=subtask_id)
    if not toggled:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subtask with ID {subtask_id} not found",
        )
    return toggled
