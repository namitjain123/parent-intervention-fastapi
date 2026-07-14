import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

load_dotenv()
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

connect_args = {"check_same_thread": False} if SQLALCHEMY_DATABASE_URL.startswith("sqlite") else {}
#Think of the engine as the main database connection manager.
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args=connect_args)
#A session is like a temporary conversation with the database. It allows you to query and manipulate data. SessionLocal is a factory for creating new sessions.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

#function is used in FastAPI as a dependency. It creates a new database session for each request and ensures that the session is properly closed after the request is finished, preventing potential database connection leaks.
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()