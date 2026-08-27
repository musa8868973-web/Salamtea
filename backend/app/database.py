"""
Database engine & session factory.

Uses SQLite by default (zero-config dev setup).
Switch to PostgreSQL in production by setting DATABASE_URL in .env:

    DATABASE_URL=postgresql://user:password@localhost:5432/salamtea_db
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL: str = os.getenv(
    "DATABASE_URL", "sqlite:///./salamtea.db"
)

# SQLite requires check_same_thread=False; PostgreSQL ignores the kwarg
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args,
    pool_pre_ping=True,   # detect stale connections
    echo=False,            # set True to log SQL in dev
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


# ── Dependency injected into route handlers ───────────────────────────────────
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
