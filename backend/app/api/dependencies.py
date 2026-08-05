from collections.abc import Generator

from sqlalchemy.orm import Session

from app.connections.connection import SessionLocal
from app.repository.implementations.sqlalchemy_product_repository import (
    SQLAlchemyProductRepository,
)
from app.service.product_service import ProductService


def get_db() -> Generator[Session, None, None]:

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def get_product_service() -> Generator[
    ProductService,
    None,
    None,
]:

    db = SessionLocal()

    try:
        repository = SQLAlchemyProductRepository(
            db
        )

        service = ProductService(
            repository
        )

        yield service

    finally:
        db.close()