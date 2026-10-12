from typing import List, Optional
from fastapi import HTTPException, status
from sqlmodel import Session, select

from backend.app.models.subtask import Subtask
from backend.app.models.todo import Todo
from backend.app.schemas.subtask import SubtaskCreate, SubtaskRead, SubtaskUpdate


class SubtaskService:
    @staticmethod
    def get_subtasks_for_todo(session: Session, todo_id: int) -> List[SubtaskRead]:
        statement = select(Subtask).where(Subtask.todo_id == todo_id).order_by(Subtask.id.asc())
        subtasks = session.exec(statement).all()
        return [SubtaskRead.model_validate(s) for s in subtasks]

    @staticmethod
    def create_subtask(session: Session, todo_id: int, subtask_in: SubtaskCreate) -> SubtaskRead:
        todo = session.get(Todo, todo_id)
        if not todo:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Todo with id {todo_id} not found",
            )
        subtask = Subtask(
            todo_id=todo_id,
            title=subtask_in.title.strip(),
            is_completed=subtask_in.is_completed,
        )
        session.add(subtask)
        session.commit()
        session.refresh(subtask)
        return SubtaskRead.model_validate(subtask)

    @staticmethod
    def update_subtask(session: Session, subtask_id: int, subtask_in: SubtaskUpdate) -> SubtaskRead:
        subtask = session.get(Subtask, subtask_id)
        if not subtask:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Subtask with id {subtask_id} not found",
            )
        if subtask_in.title is not None:
            subtask.title = subtask_in.title.strip()
        if subtask_in.is_completed is not None:
            subtask.is_completed = subtask_in.is_completed

        session.add(subtask)
        session.commit()
        session.refresh(subtask)
        return SubtaskRead.model_validate(subtask)

    @staticmethod
    def toggle_subtask(session: Session, subtask_id: int) -> SubtaskRead:
        subtask = session.get(Subtask, subtask_id)
        if not subtask:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Subtask with id {subtask_id} not found",
            )
        subtask.is_completed = not subtask.is_completed
        session.add(subtask)
        session.commit()
        session.refresh(subtask)
        return SubtaskRead.model_validate(subtask)

    @staticmethod
    def delete_subtask(session: Session, subtask_id: int) -> bool:
        subtask = session.get(Subtask, subtask_id)
        if not subtask:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Subtask with id {subtask_id} not found",
            )
        session.delete(subtask)
        session.commit()
        return True
