from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.api.dependencies import get_product_service
from app.api.product_routes import router
from app.models.product import Product

class FakeService:
    def get_products(self, skip=0, limit=20):
        return [Product(id=1, product_name="Black Shirt", category="shirts", price=1999.0, rating=4.5)]
    def get_product(self, product_id):
        return Product(id=1, product_name="Black Shirt", rating=4.5) if product_id == 1 else None
    def get_products_by_category(self, category, skip=0, limit=20):
        return [Product(id=1, product_name="Black Shirt", category=category)]
    def create_product(self, product):
        return Product(id=10, **product.model_dump())
    def update_product(self, product_id, product):
        if product_id != 1:
            return None
        data = dict(product_name="Black Shirt", category=None, price=None, description=None,
                    image_url=None, product_url=None, gender=None, rating=None)
        data.update(product.model_dump(exclude_unset=True))
        return Product(id=1, **data)
    def delete_product(self, product_id):
        return product_id == 1

app = FastAPI()
app.include_router(router, prefix="/api")
app.dependency_overrides[get_product_service] = lambda: FakeService()
client = TestClient(app)

def test_get_products():
    r = client.get("/api/products")
    assert r.status_code == 200
    assert r.json()[0]["product_name"] == "Black Shirt"

def test_get_product():
    assert client.get("/api/products/1").status_code == 200

def test_get_product_not_found():
    assert client.get("/api/products/999").status_code == 404

def test_get_by_category():
    r = client.get("/api/products/category/shirts")
    assert r.status_code == 200
    assert r.json()[0]["category"] == "shirts"

def test_create_product():
    r = client.post("/api/products", json={"product_name":"New Shirt","rating":4.1})
    assert r.status_code == 201
    assert r.json()["id"] == 10

def test_update_product():
    r = client.patch("/api/products/1", json={"price":2499.0})
    assert r.status_code == 200
    assert r.json()["price"] == 2499.0

def test_update_not_found():
    assert client.patch("/api/products/999", json={"price":2499.0}).status_code == 404

def test_delete_product():
    assert client.delete("/api/products/1").status_code == 200

def test_delete_not_found():
    assert client.delete("/api/products/999").status_code == 404
