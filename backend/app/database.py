"""
Database engine & session factory.

Uses SQLite by default (zero-config dev setup).
Switch to PostgreSQL in production by setting DATABASE_URL in .env:

    DATABASE_URL=postgresql://user:password@localhost:5432/salamtea_db
"""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

# Prefer a DATABASE_URL environment variable (Railway PostgreSQL plugin)
database_url = os.getenv("DATABASE_URL")

if database_url:
    # For databases like PostgreSQL, SQLAlchemy accepts DATABASE_URL directly
    engine = create_engine(database_url, future=True)
else:
    # Fall back to local SQLite for development
    db_path = os.path.join(os.path.dirname(__file__), "..", "salamtea.db")
    sqlite_url = f"sqlite:///{os.path.abspath(db_path)}"
    engine = create_engine(sqlite_url, connect_args={"check_same_thread": False}, future=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)



