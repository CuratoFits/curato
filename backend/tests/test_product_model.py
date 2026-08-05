from app.models.product import Product

def test_product_table_name():
    assert Product.__tablename__ == "products"

def test_product_columns():
    expected = {"id","product_name","category","price","description","image_url",
                "product_url","gender","rating","created_at","updated_at"}
    assert expected.issubset(set(Product.__table__.columns.keys()))

def test_product_primary_key():
    assert Product.__table__.c.id.primary_key is True

def test_product_name_required():
    assert Product.__table__.c.product_name.nullable is False

def test_product_url_unique():
    assert Product.__table__.c.product_url.unique is True
