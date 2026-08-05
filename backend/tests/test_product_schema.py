import pytest
from pydantic import ValidationError
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate

def test_product_create_schema():
    p = ProductCreate(product_name="Black Oversized Shirt", category="shirts",
                      price=1999.0, rating=4.5)
    assert p.product_name == "Black Oversized Shirt"
    assert p.rating == 4.5

def test_product_optional_fields():
    p = ProductCreate(product_name="Basic T-Shirt")
    assert p.category is None
    assert p.rating is None

def test_product_name_required():
    with pytest.raises(ValidationError):
        ProductCreate()

def test_product_update_is_partial():
    p = ProductUpdate(price=2499.0)
    assert p.price == 2499.0
    assert p.product_name is None

def test_product_response_from_attributes():
    class Obj:
        id=1; product_name="Shirt"; category=None; price=1000.0
        description=None; image_url=None; product_url=None; gender=None; rating=4.2
    p = ProductResponse.model_validate(Obj())
    assert p.id == 1
    assert p.rating == 4.2
