from abc import ABC, abstractmethod

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


class ProductRepository(ABC):

    @abstractmethod
    def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Product]:
        pass

    @abstractmethod
    def get_by_id(
        self,
        product_id: int,
    ) -> Product | None:
        pass

    @abstractmethod
    def get_by_category(
        self,
        category: str,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Product]:
        pass

    @abstractmethod
    def create(
        self,
        product: ProductCreate,
    ) -> Product:
        pass

    @abstractmethod
    def update(
        self,
        product_id: int,
        product: ProductUpdate,
    ) -> Product | None:
        pass

    @abstractmethod
    def delete(
        self,
        product_id: int,
    ) -> bool:
        pass