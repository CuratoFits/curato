from pydantic import BaseModel, Field

from app.models.model import ItemCategory, UserRole


class LoginRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=100)
    password: str = Field(..., min_length=4)


class LoginResponse(BaseModel):
    message: str
    role: UserRole
    user_id: int


class ItemCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=200)
    category: ItemCategory
    price: float = Field(..., gt=0)
    stock: int = Field(..., ge=0)
    description: str | None = None
    image_url: str | None = None


class ItemUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    category: ItemCategory | None = None
    price: float | None = Field(default=None, gt=0)
    stock: int | None = Field(default=None, ge=0)
    description: str | None = None
    image_url: str | None = None


class ItemResponse(BaseModel):
    id: int
    name: str
    category: ItemCategory
    price: float
    stock: int
    description: str | None = None
    image_url: str | None = None


class CartItemRequest(BaseModel):
    item_id: int
    quantity: int = Field(default=1, ge=1)


class CartItemResponse(BaseModel):
    id: int
    user_id: int
    item_id: int
    quantity: int


class MessageResponse(BaseModel):
    message: str
