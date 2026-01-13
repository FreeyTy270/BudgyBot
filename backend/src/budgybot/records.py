import os

from sqlmodel import SQLModel, create_engine, Session


# Database URL: defaults to local SQLite if not provided
DB_URL = os.getenv("DATABASE_URL", "sqlite:///budgybot.db")

# Create SQLModel / SQLAlchemy engine
engine = create_engine(DB_URL, echo=True)


def create_db_and_tables() -> None:
    """Create all tables defined on SQLModel metadata."""
    SQLModel.metadata.create_all(engine)


def get_session():
    """FastAPI dependency that yields a database session."""
    with Session(engine) as session:
        yield session
