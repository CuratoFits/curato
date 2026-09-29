from pydantic import BaseModel, ConfigDict


class ProductBase(BaseModel):
    product_name: str
    category: str | None = None
    subcategory: str | None = None
    brand: str | None = None
    gender: str | None = None
    price: float | None = None
    original_price: float | None = None
    discount: float | None = None
    color: str | None = None
    material: str | None = None
    style: str | None = None
    occasion: str | None = None
    fit: str | None = None
    season: str | None = None
    description: str | None = None
    rating: float | None = None
    availability: str | None = None
    image_url: str | None = None
    product_url: str | None = None


class ProductCreate(ProductBase):
    pass


class ProductUpdate(BaseModel):
    product_name: str | None = None
    category: str | None = None
    subcategory: str | None = None
    brand: str | None = None
    gender: str | None = None
    price: float | None = None
    original_price: float | None = None
    discount: float | None = None
    color: str | None = None
    material: str | None = None
    style: str | None = None
    occasion: str | None = None
    fit: str | None = None
    season: str | None = None
    description: str | None = None
    rating: float | None = None
    availability: str | None = None
    image_url: str | None = None
    product_url: str | None = None


class ProductResponse(ProductBase):
    id: int

    model_config = ConfigDict(from_attributes=True)