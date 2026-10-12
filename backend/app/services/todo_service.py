from datetime import datetime, timezone
import math
from typing import List, Optional, Tuple
from sqlalchemy import func, or_, text
from sqlmodel import Session, select

from backend.app.models.enums import Priority, Status
from backend.app.models.todo import Todo
from backend.app.models.category import Category
from backend.app.schemas.category import CategoryRead
from backend.app.schemas.subtask import SubtaskRead
from backend.app.schemas.todo import TodoCreate, TodoRead, TodoUpdate
from backend.app.services.category_service import CategoryService


class TodoService:
    @staticmethod
    def _is_overdue(todo: Todo) -> bool:
        if not todo.due_date or todo.status == Status.COMPLETED:
            return False
        # Normalize datetime timezone
        now = datetime.now(timezone.utc)
        due = todo.due_date
        if due.tzinfo is None:
            due = due.replace(tzinfo=timezone.utc)
        return due < now

    @staticmethod
    def _get_subtasks_and_stats(session: Session, todo_id: int) -> Tuple[List[SubtaskRead], int, int, float]:
        """Safely fetch subtasks list and progress stats."""
        try:
            from backend.app.models.subtask import Subtask
            stmt = select(Subtask).where(Subtask.todo_id == todo_id).order_by(Subtask.created_at.asc())
            subtasks = session.exec(stmt).all()
            subtasks_read = [SubtaskRead.model_validate(st) for st in subtasks]
            total = len(subtasks)
            completed = sum(1 for st in subtasks if st.is_completed)
            percentage = round((completed / total) * 100.0, 1) if total > 0 else 0.0
            return subtasks_read, total, completed, percentage
        except Exception:
            return [], 0, 0, 0.0

    @classmethod
    def enrich_todo(cls, session: Session, todo: Todo) -> TodoRead:
        subtasks_read, subtasks_count, subtasks_completed_count, progress_percentage = cls._get_subtasks_and_stats(
            session, todo.id
        )
        is_overdue = cls._is_overdue(todo)
        is_completed = (todo.status == Status.COMPLETED)

        category_read = None
        if todo.category_id:
            category = session.get(Category, todo.category_id)
            if category:
                category_read = CategoryRead(
                    id=category.id,
                    name=category.name,
                    color=category.color,
                    icon=category.icon,
                    created_at=category.created_at,
                    todos_count=0,
                )

        return TodoRead(
            id=todo.id,
            title=todo.title,
            description=todo.description,
            priority=todo.priority,
            status=todo.status,
            is_completed=is_completed,
            due_date=todo.due_date,
            tags=todo.tags,
            category_id=todo.category_id,
            category=category_read,
            created_at=todo.created_at,
            updated_at=todo.updated_at,
            completed_at=todo.completed_at,
            subtasks=subtasks_read,
            subtasks_count=subtasks_count,
            subtasks_completed_count=subtasks_completed_count,
            progress_percentage=progress_percentage,
            is_overdue=is_overdue,
        )

    @classmethod
    def create_todo(cls, session: Session, todo_in: TodoCreate) -> TodoRead:
        category_id = todo_in.category_id
        if not category_id and todo_in.category_name:
            cat = CategoryService.get_or_create(session, todo_in.category_name)
            category_id = cat.id

        status = todo_in.status
        if todo_in.is_completed is True:
            status = Status.COMPLETED
        elif todo_in.is_completed is False and status == Status.COMPLETED:
            status = Status.PENDING

        now = datetime.now(timezone.utc)
        completed_at = now if status == Status.COMPLETED else None

        todo = Todo(
            title=todo_in.title.strip(),
            description=todo_in.description.strip() if todo_in.description else None,
            priority=todo_in.priority,
            status=status,
            due_date=todo_in.due_date,
            tags=todo_in.tags,
            category_id=category_id,
            created_at=now,
            updated_at=now,
            completed_at=completed_at,
        )

        session.add(todo)
        session.commit()
        session.refresh(todo)
        return cls.enrich_todo(session, todo)

    @classmethod
    def get_todo(cls, session: Session, todo_id: int) -> Optional[TodoRead]:
        todo = session.get(Todo, todo_id)
        if not todo:
            return None
        return cls.enrich_todo(session, todo)

    @classmethod
    def list_todos(
        cls,
        session: Session,
        status: Optional[Status] = None,
        priority: Optional[Priority] = None,
        category_id: Optional[int] = None,
        category: Optional[str] = None,
        search: Optional[str] = None,
        is_completed: Optional[bool] = None,
        page: int = 1,
        limit: int = 50,
        sort_by: str = "created_at_desc",
    ) -> Tuple[List[TodoRead], int]:
        query = select(Todo)

        if is_completed is True:
            query = query.where(Todo.status == Status.COMPLETED)
        elif is_completed is False:
            query = query.where(Todo.status != Status.COMPLETED)
        elif status:
            query = query.where(Todo.status == status)

        if priority:
            query = query.where(Todo.priority == priority)
        if category_id:
            query = query.where(Todo.category_id == category_id)
        elif category and category.strip():
            query = query.join(Category, Todo.category_id == Category.id).where(
                Category.name.ilike(category.strip())
            )
        if search and search.strip():
            term = f"%{search.strip()}%"
            query = query.where(
                or_(
                    Todo.title.ilike(term),
                    Todo.description.ilike(term),
                    Todo.tags.ilike(term),
                )
            )

        # Count total matches before pagination
        count_stmt = select(func.count()).select_from(query.subquery())
        total = session.exec(count_stmt).one()

        # Sorting logic
        if sort_by == "due_date_asc":
            query = query.order_by(Todo.due_date.asc().nullslast())
        elif sort_by == "due_date_desc":
            query = query.order_by(Todo.due_date.desc().nullslast())
        elif sort_by == "priority_desc":
            query = query.order_by(Todo.priority.desc())
        elif sort_by == "created_at_asc":
            query = query.order_by(Todo.created_at.asc())
        else:
            query = query.order_by(Todo.created_at.desc())

        # Pagination offsets
        safe_page = max(page, 1)
        safe_limit = max(1, min(limit, 100))
        offset = (safe_page - 1) * safe_limit

        query = query.offset(offset).limit(safe_limit)
        todos = session.exec(query).all()

        enriched = [cls.enrich_todo(session, t) for t in todos]
        return enriched, total

    @classmethod
    def update_todo(
        cls,
        session: Session,
        todo_id: int,
        todo_in: TodoUpdate,
    ) -> Optional[TodoRead]:
        todo = session.get(Todo, todo_id)
        if not todo:
            return None

        update_data = todo_in.model_dump(exclude_unset=True)
        # Handle is_completed explicitly
        is_comp = update_data.pop("is_completed", None)

        for key, val in update_data.items():
            setattr(todo, key, val)

        now = datetime.now(timezone.utc)
        todo.updated_at = now

        if is_comp is not None:
            if is_comp:
                todo.status = Status.COMPLETED
                todo.completed_at = now
            else:
                todo.status = Status.PENDING
                todo.completed_at = None
        elif todo_in.status is not None:
            if todo_in.status == Status.COMPLETED and not todo.completed_at:
                todo.completed_at = now
            elif todo_in.status != Status.COMPLETED:
                todo.completed_at = None

        session.add(todo)
        session.commit()
        session.refresh(todo)
        return cls.enrich_todo(session, todo)

    @classmethod
    def toggle_todo(cls, session: Session, todo_id: int) -> Optional[TodoRead]:
        todo = session.get(Todo, todo_id)
        if not todo:
            return None

        now = datetime.now(timezone.utc)
        if todo.status == Status.COMPLETED:
            todo.status = Status.PENDING
            todo.completed_at = None
        else:
            todo.status = Status.COMPLETED
            todo.completed_at = now

        todo.updated_at = now
        session.add(todo)
        session.commit()
        session.refresh(todo)
        return cls.enrich_todo(session, todo)

    @classmethod
    def delete_todo(cls, session: Session, todo_id: int) -> bool:
        todo = session.get(Todo, todo_id)
        if not todo:
            return False

        # Clean up associated subtasks
        try:
            from backend.app.models.subtask import Subtask
            subtasks = session.exec(select(Subtask).where(Subtask.todo_id == todo_id)).all()
            for st in subtasks:
                session.delete(st)
        except Exception:
            pass

        session.delete(todo)
        session.commit()
        return True
