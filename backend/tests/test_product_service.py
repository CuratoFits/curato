from unittest.mock import MagicMock
from app.models.product import Product
from app.repository.interfaces.product_repository import ProductRepository
from app.schemas.product import ProductCreate, ProductUpdate
from app.service.product_service import ProductService

def repo_mock():
    return MagicMock(spec=ProductRepository)

def test_get_products():
    repo = repo_mock()
    repo.get_all.return_value = [Product(id=1, product_name="Shirt")]
    service = ProductService(repo)
    assert len(service.get_products(0, 20)) == 1
    repo.get_all.assert_called_once_with(skip=0, limit=20)

def test_get_product():
    repo = repo_mock()
    expected = Product(id=1, product_name="Shirt")
    repo.get_by_id.return_value = expected
    assert ProductService(repo).get_product(1) is expected

def test_get_by_category():
    repo = repo_mock()
    repo.get_by_category.return_value = []
    ProductService(repo).get_products_by_category("shirts", 0, 20)
    repo.get_by_category.assert_called_once_with(category="shirts", skip=0, limit=20)

def test_create_product():
    repo = repo_mock()
    payload = ProductCreate(product_name="Shirt")
    expected = Product(id=1, product_name="Shirt")
    repo.create.return_value = expected
    assert ProductService(repo).create_product(payload) is expected

def test_update_product():
    repo = repo_mock()
    payload = ProductUpdate(price=2000.0)
    ProductService(repo).update_product(1, payload)
    repo.update.assert_called_once_with(1, payload)

def test_delete_product():
    repo = repo_mock()
    repo.delete.return_value = True
    assert ProductService(repo).delete_product(1) is True
