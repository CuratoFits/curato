from unittest.mock import MagicMock
from app.models.product import Product
from app.repository.implementations.sqlalchemy_product_repository import SQLAlchemyProductRepository
from app.schemas.product import ProductCreate, ProductUpdate

def test_get_by_id():
    db = MagicMock()
    expected = Product(id=1, product_name="Shirt")
    db.get.return_value = expected
    repo = SQLAlchemyProductRepository(db)
    assert repo.get_by_id(1) is expected
    db.get.assert_called_once_with(Product, 1)

def test_create():
    db = MagicMock()
    repo = SQLAlchemyProductRepository(db)
    payload = ProductCreate(product_name="Shirt", rating=4.5)
    result = repo.create(payload)
    assert result.product_name == "Shirt"
    db.add.assert_called_once_with(result)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(result)

def test_update_missing():
    db = MagicMock()
    db.get.return_value = None
    repo = SQLAlchemyProductRepository(db)
    assert repo.update(999, ProductUpdate(price=2000.0)) is None
    db.commit.assert_not_called()

def test_update():
    db = MagicMock()
    existing = Product(id=1, product_name="Old", price=1000.0)
    db.get.return_value = existing
    repo = SQLAlchemyProductRepository(db)
    result = repo.update(1, ProductUpdate(product_name="New", price=1500.0))
    assert result.product_name == "New"
    assert result.price == 1500.0
    db.commit.assert_called_once()

def test_delete_missing():
    db = MagicMock()
    db.get.return_value = None
    repo = SQLAlchemyProductRepository(db)
    assert repo.delete(999) is False
    db.delete.assert_not_called()

def test_delete():
    db = MagicMock()
    existing = Product(id=1, product_name="Shirt")
    db.get.return_value = existing
    repo = SQLAlchemyProductRepository(db)
    assert repo.delete(1) is True
    db.delete.assert_called_once_with(existing)
    db.commit.assert_called_once()
