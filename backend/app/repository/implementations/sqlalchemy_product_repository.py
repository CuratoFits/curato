from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate
from app.repository.interfaces.product_repository import (
    ProductRepository,
)


class SQLAlchemyProductRepository(ProductRepository):

    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Product]:

        statement = (
            select(Product)
            .offset(skip)
            .limit(limit)
        )

        return list(
            self.db.scalars(statement).all()
        )

    def get_by_id(
        self,
        product_id: int,
    ) -> Product | None:

        return self.db.get(
            Product,
            product_id,
        )

    def get_by_category(
        self,
        category: str,
        skip: int = 0,
        limit: int = 20,
    ) -> list[Product]:

        statement = (
            select(Product)
            .where(Product.category == category)
            .offset(skip)
            .limit(limit)
        )

        return list(
            self.db.scalars(statement).all()
        )

    def create(
        self,
        product: ProductCreate,
    ) -> Product:

        db_product = Product(
            **product.model_dump()
        )

        self.db.add(db_product)
        self.db.commit()
        self.db.refresh(db_product)

        return db_product

    def update(
        self,
        product_id: int,
        product: ProductUpdate,
    ) -> Product | None:

        db_product = self.get_by_id(product_id)

        if db_product is None:
            return None

        update_data = product.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():
            setattr(
                db_product,
                field,
                value,
            )

        self.db.commit()
        self.db.refresh(db_product)

        return db_product

    def delete(
        self,
        product_id: int,
    ) -> bool:

        db_product = self.get_by_id(product_id)

        if db_product is None:
            return False

        self.db.delete(db_product)
        self.db.commit()

        return True