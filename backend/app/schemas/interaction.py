from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


# Allowed interaction event types
EventType = Literal[
    "view",
    "click",
    "wishlist",
    "add_to_cart",
    "purchase",
    "not_interested",
]


# Allowed interaction sources
InteractionSource = Literal[
    "category",
    "homepage",
    "product_page",
    "recommendation",
    "search",
]


class InteractionEventCreate(BaseModel):

    user_id: int = Field(gt=0)

    product_id: int = Field(gt=0)

    event_type: EventType

    session_id: str = Field(
        min_length=1
    )

    time_spent_seconds: float = Field(
        ge=0
    )

    scroll_depth: float = Field(
        ge=0,
        le=100,
    )

    source: InteractionSource

    quantity: int = Field(
        ge=1
    )

    timestamp: datetime


class InteractionEventUpdate(BaseModel):

    event_type: EventType | None = None

    time_spent_seconds: float | None = Field(
        default=None,
        ge=0,
    )

    scroll_depth: float | None = Field(
        default=None,
        ge=0,
        le=100,
    )

    source: InteractionSource | None = None

    quantity: int | None = Field(
        default=None,
        ge=1,
    )

    timestamp: datetime | None = None


class InteractionEventResponse(BaseModel):

    model_config = ConfigDict(
        from_attributes=True
    )

    event_id: int

    user_id: int

    product_id: int

    event_type: EventType

    session_id: str

    time_spent_seconds: float

    scroll_depth: float

    source: InteractionSource

    quantity: int

    timestamp: datetime