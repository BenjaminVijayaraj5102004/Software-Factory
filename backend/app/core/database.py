from typing import Generator
from sqlmodel import Session, SQLModel, create_engine
from backend.app.core.config import settings

# SQLite requires check_same_thread=False for multi-threaded FastAPI request handling
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    echo=False,
    connect_args=connect_args,
)


def init_db() -> None:
    """Initialize database tables from SQLModel metadata."""
    import backend.app.models  # noqa: F401
    SQLModel.metadata.create_all(engine)


create_db_and_tables = init_db


def get_session() -> Generator[Session, None, None]:
    with Session(engine) as session:
        yield session
