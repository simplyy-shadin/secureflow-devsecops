from collections.abc import Generator

from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings


class Base(DeclarativeBase):
    """Base class for SQLAlchemy ORM models."""


def create_database_engine(database_url: str) -> Engine:
    """Create a database engine with SQLite-safe defaults for local development."""
    connect_args = (
        {"check_same_thread": False}
        if database_url.startswith("sqlite")
        else {}
    )

    return create_engine(
        database_url,
        connect_args=connect_args,
        pool_pre_ping=True,
    )


settings = get_settings()
engine = create_database_engine(settings.database_url)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    expire_on_commit=False,
)


def get_db() -> Generator[Session, None, None]:
    """Provide a database session and guarantee it is closed after the request."""
    with SessionLocal() as session:
        yield session
