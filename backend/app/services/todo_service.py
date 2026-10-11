from datetime import datetime, timezone
import math
from typing import List, Optional, Tuple
from sqlalchemy import func, or_, text
from sqlmodel import Session, select

from backend.app.models.enums import Priority, Status
from backend.app.models.todo import Todo
from backend.app.models.category import Category
from backend.app.schemas.category import CategoryRead
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
    def _get_subtask_stats(session: Session, todo_id: int) -> Tuple[int, int, float]:
        """Safely fetch subtask counts if subtask module/table is active."""
        try:
            query = text(
                "SELECT COUNT(*), SUM(CASE WHEN is_completed = 1 THEN 1 ELSE 0 END) "
                "FROM subtasks WHERE todo_id = :tid"
            )
            result = session.exec(query, params={"tid": todo_id}).first()
            if result and result[0] is not None:
                total = int(result[0])
                completed = int(result[1] or 0)
                percentage = round((completed / total) * 100.0, 1) if total > 0 else 0.0
                return total, completed, percentage
        except Exception:
            pass
        return 0, 0, 0.0

    @classmethod
    def enrich_todo(cls, session: Session, todo: Todo) -> TodoRead:
        subtasks_count, subtasks_completed_count, progress_percentage = cls._get_subtask_stats(
            session, todo.id
        )
        is_overdue = cls._is_overdue(todo)

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
            due_date=todo.due_date,
            tags=todo.tags,
            category_id=todo.category_id,
            category=category_read,
            created_at=todo.created_at,
            updated_at=todo.updated_at,
            completed_at=todo.completed_at,
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

        now = datetime.now(timezone.utc)
        completed_at = now if todo_in.status == Status.COMPLETED else None

        todo = Todo(
            title=todo_in.title.strip(),
            description=todo_in.description.strip() if todo_in.description else None,
            priority=todo_in.priority,
            status=todo_in.status,
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
        page: int = 1,
        limit: int = 50,
        sort_by: str = "created_at_desc",
    ) -> Tuple[List[TodoRead], int]:
        query = select(Todo)

        if status:
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
        for key, val in update_data.items():
            setattr(todo, key, val)

        now = datetime.now(timezone.utc)
        todo.updated_at = now

        # Update completed_at timestamp tracking
        if todo_in.status is not None:
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

        # If subtasks table exists, clean up associated subtasks
        try:
            session.exec(
                text("DELETE FROM subtasks WHERE todo_id = :tid"),
                params={"tid": todo_id},
            )
        except Exception:
            pass

        session.delete(todo)
        session.commit()
        return True
