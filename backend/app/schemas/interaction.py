from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

EventType = Literal["view", "click", "wishlist", "add_to_cart", "purchase", "not_interested"]
EventSource = Literal["homepage", "search", "category", "product_page", "recommendation"]


class InteractionEventBase(BaseModel):
    user_id: int = Field(gt=0)
    product_id: int = Field(gt=0)
    event_type: EventType
    session_id: str = Field(min_length=1, max_length=100)
    time_spent_seconds: float = Field(ge=0)
    scroll_depth: float = Field(ge=0, le=100)
    source: EventSource
    quantity: int = Field(ge=1)
    timestamp: datetime


class InteractionEventCreate(InteractionEventBase):
    pass


class InteractionEventUpdate(BaseModel):
    user_id: int | None = Field(default=None, gt=0)
    product_id: int | None = Field(default=None, gt=0)
    event_type: EventType | None = None
    session_id: str | None = Field(default=None, min_length=1, max_length=100)
    time_spent_seconds: float | None = Field(default=None, ge=0)
    scroll_depth: float | None = Field(default=None, ge=0, le=100)
    source: EventSource | None = None
    quantity: int | None = Field(default=None, ge=1)
    timestamp: datetime | None = None


class InteractionEventResponse(InteractionEventBase):
    event_id: int

    model_config = ConfigDict(from_attributes=True)