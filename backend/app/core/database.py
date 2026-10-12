import os
import sqlite3
from typing import Generator
from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine, select

from backend.app.core.config import settings

# If SQLite database URL points to a relative or absolute directory, ensure it exists
if settings.DATABASE_URL.startswith("sqlite:///"):
    db_file_path = settings.DATABASE_URL.replace("sqlite:///", "")
    dir_name = os.path.dirname(db_file_path)
    if dir_name and not os.path.exists(dir_name):
        os.makedirs(dir_name, exist_ok=True)

# SQLite requires check_same_thread=False for multi-threaded FastAPI request handling
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    connect_args=connect_args,
)


@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    """Enable foreign key constraints and WAL mode for high-concurrency SQLite operations."""
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA synchronous=NORMAL;")
        cursor.close()


def init_db() -> None:
    """Initialize database tables from SQLModel metadata and seed default categories."""
    import backend.app.models  # noqa: F401
    from backend.app.models.category import Category

    SQLModel.metadata.create_all(engine)

    # Seed default categories if database is newly initialized
    with Session(engine) as session:
        existing = session.exec(select(Category)).first()
        if not existing:
            defaults = [
                Category(name="Work", color="#3B82F6"),
                Category(name="Personal", color="#10B981"),
                Category(name="Urgent", color="#EF4444"),
                Category(name="Study", color="#8B5CF6"),
            ]
            for cat in defaults:
                session.add(cat)
            session.commit()


create_db_and_tables = init_db


def get_session() -> Generator[Session, None, None]:
    """Dependency injection session generator."""
    with Session(engine) as session:
        yield session
