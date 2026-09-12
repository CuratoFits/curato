from pydantic import BaseModel, ConfigDict


class ProductBase(BaseModel):
    product_name: str
    category: str | None = None
    price: float | None = None
    description: str | None = None
    image_url: str | None = None
    product_url: str | None = None
    gender: str | None = None
    rating: float | None = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    product_name: str | None = None
    category: str | None = None
    price: float | None = None
    description: str | None = None
    image_url: str | None = None
    product_url: str | None = None
    gender: str | None = None
    rating: float | None = None


class ProductResponse(ProductBase):
    id: int

    model_config = ConfigDict(
        from_attributes=True
    )