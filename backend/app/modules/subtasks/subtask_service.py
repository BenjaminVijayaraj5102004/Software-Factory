from datetime import datetime, timezone
from typing import List, Optional, Tuple
from sqlmodel import Session, select

from backend.app.models.todo import Todo
from backend.app.models.subtask import Subtask
from backend.app.schemas.subtask import SubtaskCreate, SubtaskRead, SubtaskUpdate


class SubtaskService:
    @classmethod
    def list_subtasks(cls, session: Session, todo_id: int) -> List[SubtaskRead]:
        """Fetch all subtasks for a given todo item."""
        statement = select(Subtask).where(Subtask.todo_id == todo_id).order_by(Subtask.created_at.asc())
        subtasks = session.exec(statement).all()
        return [SubtaskRead.model_validate(st) for st in subtasks]

    @classmethod
    def get_subtask(cls, session: Session, subtask_id: int) -> Optional[SubtaskRead]:
        """Retrieve a specific subtask by ID."""
        subtask = session.get(Subtask, subtask_id)
        if not subtask:
            return None
        return SubtaskRead.model_validate(subtask)

    @classmethod
    def create_subtask(
        cls, session: Session, todo_id: int, subtask_in: SubtaskCreate
    ) -> Optional[SubtaskRead]:
        """Create a new subtask attached to a parent todo."""
        todo = session.get(Todo, todo_id)
        if not todo:
            return None

        subtask = Subtask(
            title=subtask_in.title.strip(),
            is_completed=subtask_in.is_completed,
            todo_id=todo_id,
            created_at=datetime.now(timezone.utc),
        )
        session.add(subtask)
        session.commit()
        session.refresh(subtask)
        return SubtaskRead.model_validate(subtask)

    @classmethod
    def update_subtask(
        cls, session: Session, subtask_id: int, subtask_in: SubtaskUpdate
    ) -> Optional[SubtaskRead]:
        """Update subtask fields (e.g. toggle completion or edit title)."""
        subtask = session.get(Subtask, subtask_id)
        if not subtask:
            return None

        update_data = subtask_in.model_dump(exclude_unset=True)
        for key, val in update_data.items():
            setattr(subtask, key, val)

        session.add(subtask)
        session.commit()
        session.refresh(subtask)
        return SubtaskRead.model_validate(subtask)

    @classmethod
    def toggle_subtask(cls, session: Session, subtask_id: int) -> Optional[SubtaskRead]:
        """Toggle subtask completion status."""
        subtask = session.get(Subtask, subtask_id)
        if not subtask:
            return None

        subtask.is_completed = not subtask.is_completed
        session.add(subtask)
        session.commit()
        session.refresh(subtask)
        return SubtaskRead.model_validate(subtask)

    @classmethod
    def delete_subtask(cls, session: Session, subtask_id: int) -> bool:
        """Delete a subtask by ID."""
        subtask = session.get(Subtask, subtask_id)
        if not subtask:
            return False

        session.delete(subtask)
        session.commit()
        return True

    @classmethod
    def get_progress(cls, session: Session, todo_id: int) -> Tuple[int, int, float]:
        """Return total, completed, and percentage for a todo's subtasks."""
        subtasks = session.exec(select(Subtask).where(Subtask.todo_id == todo_id)).all()
        total = len(subtasks)
        completed = sum(1 for st in subtasks if st.is_completed)
        percentage = round((completed / total) * 100.0, 1) if total > 0 else 0.0
        return total, completed, percentage
