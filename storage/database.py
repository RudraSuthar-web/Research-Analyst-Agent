"""
storage/database.py
SQLite metadata store — tracks every ingested document.
"""
from datetime import datetime
from pathlib import Path

from sqlalchemy import (
    create_engine, Column, String, Text, DateTime, Integer, JSON
)
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session

from utils.config import settings


class Base(DeclarativeBase):
    pass


class Document(Base):
    """One row per ingested source (PDF, URL, or text file)."""
    __tablename__ = "documents"

    id          = Column(String, primary_key=True)   # sha256 of content
    title       = Column(String, nullable=False)
    source_type = Column(String, nullable=False)     # "pdf" | "url" | "text"
    source_path = Column(String, nullable=False)     # file path or URL
    authors     = Column(JSON,   default=list)        # ["Author A", ...]
    tags        = Column(JSON,   default=list)        # user-assigned tags
    chunk_count = Column(Integer, default=0)
    created_at  = Column(DateTime, default=datetime.utcnow)
    metadata_   = Column("metadata", JSON, default=dict)

    def __repr__(self) -> str:
        return f"<Document id={self.id[:8]}… title={self.title!r}>"


def get_engine():
    db_path = Path(settings.SQLITE_DB_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return create_engine(f"sqlite:///{db_path}", echo=False)


def init_db() -> sessionmaker:
    engine = get_engine()
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)


# Module-level session factory (initialised on first use)
_SessionFactory = None

def get_session() -> Session:
    global _SessionFactory
    if _SessionFactory is None:
        _SessionFactory = init_db()
    return _SessionFactory()
