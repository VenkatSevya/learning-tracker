"""Database connection. DATABASE_URL decides which database is used."""
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# postgresql+psycopg2://user:password@db:5432/name  -> PostgreSQL (Docker Compose)
# not set                                           -> a local SQLite file (quick runs)
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./learning.db")

connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    """One database session per request, always closed afterwards."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
