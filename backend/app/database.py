import os
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

# Prefer DATABASE_URL (e.g., provided by Railway when you add Postgres plugin)
database_url = os.getenv("DATABASE_URL")

if database_url:
    # Use production DB from environment
    engine = create_engine(database_url, future=True)
else:
    # Local fallback: SQLite file inside backend directory (development only)
    base_dir = Path(__file__).resolve().parent.parent
    sqlite_path = base_dir / "salamtea.db"
    sqlite_url = f"sqlite:///{sqlite_path}"
    engine = create_engine(sqlite_url, connect_args={"check_same_thread": False}, future=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
