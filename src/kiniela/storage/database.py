"""Database connection.

The database is chosen with the ``DATABASE_URL`` environment variable, so no credential
ever lives in the code:

- not set: a local SQLite file in ``data/kiniela.db`` (development, tests, Docker);
- set: any SQLAlchemy URL, for example the PostgreSQL database on Neon in production.
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path

from sqlalchemy import Engine, create_engine, event
from sqlalchemy.orm import Session, sessionmaker

from kiniela.storage.models import Base

# src/kiniela/storage/database.py -> repo root
PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SQLITE_PATH = PROJECT_ROOT / "data" / "kiniela.db"


def resolve_database_url(url: str | None = None) -> str:
    """Return the SQLAlchemy URL to use.

    Priority: the ``url`` argument, then ``DATABASE_URL``, then the local SQLite file.
    Providers such as Neon give ``postgres://`` or ``postgresql://`` URLs; they are
    rewritten to use the psycopg 3 driver installed with the project.
    """
    url = url or os.environ.get("DATABASE_URL", "").strip()
    if not url:
        DEFAULT_SQLITE_PATH.parent.mkdir(parents=True, exist_ok=True)
        return f"sqlite:///{DEFAULT_SQLITE_PATH.as_posix()}"
    for prefix in ("postgres://", "postgresql://"):
        if url.startswith(prefix):
            return "postgresql+psycopg://" + url.removeprefix(prefix)
    return url


@lru_cache(maxsize=4)
def _engine_for(url: str) -> Engine:
    # pool_pre_ping reconnects transparently when a serverless database (Neon) went to sleep
    engine = create_engine(url, pool_pre_ping=True)
    if engine.dialect.name == "sqlite":
        event.listen(engine, "connect", _enable_sqlite_foreign_keys)
    return engine


def _enable_sqlite_foreign_keys(dbapi_connection, _record) -> None:
    """SQLite ignores foreign keys unless each connection turns them on."""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


def get_engine(url: str | None = None) -> Engine:
    """Return a shared engine for the resolved URL (one connection pool per database)."""
    return _engine_for(resolve_database_url(url))


def init_db(engine: Engine) -> None:
    """Create the tables if they do not exist. Safe to call on every app start."""
    Base.metadata.create_all(engine)


@contextmanager
def session_scope(engine: Engine) -> Iterator[Session]:
    """Open a session that commits on success and rolls back on any error."""
    session = sessionmaker(bind=engine, expire_on_commit=False)()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
