import pytest
from app.repository.interfaces.product_repository import ProductRepository

def test_product_repository_is_abstract():
    with pytest.raises(TypeError):
        ProductRepository()
