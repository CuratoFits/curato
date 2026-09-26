import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# Project root: E:\Curato\curato
ROOT_DIR = Path(__file__).resolve().parents[3]

# Load variables from .env
load_dotenv(ROOT_DIR / ".env")


DATABASE_URL = os.getenv("DATABASE_URL") or os.getenv("SUPABASE_DATABASE_URL")
LOCAL_DATABASE_URL = os.getenv("LOCAL_DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not configured in .env"
    )


# Primary SQLAlchemy engine (Supabase or default)
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

# Optional secondary local engine
engine_local = None
SessionLocalSecondary = None

if LOCAL_DATABASE_URL:
    try:
        engine_local = create_engine(LOCAL_DATABASE_URL, pool_pre_ping=True)
        SessionLocalSecondary = sessionmaker(
            bind=engine_local,
            autoflush=False,
            autocommit=False
        )
    except Exception as e:
        print(f"Warning: Local database engine initialization skipped/failed: {e}")


def get_db():
    """
    Provides a database session.
    If LOCAL_DATABASE_URL is configured, changes will also be flushed to the local database.
    """
    db = SessionLocal()
    db_local = SessionLocalSecondary() if SessionLocalSecondary else None

    try:
        yield db
        if db_local:
            db_local.commit()
    except Exception:
        if db_local:
            db_local.rollback()
        raise
    finally:
        db.close()
        if db_local:
            db_local.close()