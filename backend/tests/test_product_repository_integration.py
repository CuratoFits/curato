import pytest

from app.connections.connection import SessionLocal
from app.repository.implementations.sqlalchemy_product_repository import (
    SQLAlchemyProductRepository,
)
from app.schemas.product import ProductCreate, ProductUpdate


@pytest.fixture
def repository():
    db = SessionLocal()

    try:
        yield SQLAlchemyProductRepository(db)
    finally:
        db.close()


def test_product_crud_with_supabase(repository):
    # CREATE
    product_data = ProductCreate(
        product_name="Integration Test Product",
        category="test",
        price=1999.0,
        description="Temporary product created by pytest",
        image_url="https://example.com/test.jpg",
        product_url="https://example.com/integration-test-product",
        gender="Women",
        rating=4.5,
    )

    created_product = repository.create(product_data)

    assert created_product.id is not None
    assert created_product.product_name == "Integration Test Product"
    assert created_product.rating == 4.5

    product_id = created_product.id

    # READ
    fetched_product = repository.get_by_id(product_id)

    assert fetched_product is not None
    assert fetched_product.id == product_id
    assert fetched_product.product_name == "Integration Test Product"

    # UPDATE
    update_data = ProductUpdate(
        price=2499.0,
        rating=4.8,
    )

    updated_product = repository.update(
        product_id,
        update_data,
    )

    assert updated_product is not None
    assert updated_product.price == 2499.0
    assert updated_product.rating == 4.8

    # DELETE
    deleted = repository.delete(product_id)

    assert deleted is True

    # VERIFY DELETE
    missing_product = repository.get_by_id(product_id)

    assert missing_product is None