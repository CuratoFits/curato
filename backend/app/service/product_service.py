from app.repository.interfaces.product_repository import (
    ProductRepository,
)
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
)


class ProductService:

    def __init__(
        self,
        repository: ProductRepository,
    ):
        self.repository = repository

    def get_products(
        self,
        skip: int = 0,
        limit: int = 20,
    ):
        return self.repository.get_all(
            skip=skip,
            limit=limit,
        )

    def get_product(
        self,
        product_id: int,
    ):
        return self.repository.get_by_id(
            product_id
        )

    def get_products_by_category(
        self,
        category: str,
        skip: int = 0,
        limit: int = 20,
    ):
        return self.repository.get_by_category(
            category=category,
            skip=skip,
            limit=limit,
        )

    def create_product(
        self,
        product: ProductCreate,
    ):
        return self.repository.create(
            product
        )

    def update_product(
        self,
        product_id: int,
        product: ProductUpdate,
    ):
        return self.repository.update(
            product_id,
            product,
        )

    def delete_product(
        self,
        product_id: int,
    ):
        return self.repository.delete(
            product_id
        )