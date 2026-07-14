from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

connect_args = (
    {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
)

# Think of the engine as the main database connection manager.
engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)

# A session is like a temporary conversation with the database. It allows you
# to query and manipulate data. SessionLocal is a factory for creating new sessions.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """FastAPI dependency: opens a session per request, closes it after."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
