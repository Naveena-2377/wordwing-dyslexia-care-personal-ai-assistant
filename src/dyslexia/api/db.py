"""SQLite database setup - a single local file, no external service needed."""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from ..common.paths import ROOT

DB_PATH = ROOT / "wordwing.db"
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from . import models_db  # noqa: F401 - registers models before create_all
    Base.metadata.create_all(bind=engine)