import os
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


# Project root: E:\Curato\curato
ROOT_DIR = Path(__file__).resolve().parents[3]

# Load variables from .env
load_dotenv(ROOT_DIR / ".env")


DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "DATABASE_URL is not configured in .env"
    )


# SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True
)


# Database session factory
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


def get_db():
    """
    Provides a database session.

    FastAPI can use this function as a dependency.
    """

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()