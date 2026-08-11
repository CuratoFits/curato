from pydantic import BaseModel, ConfigDict, Field


class UserProfileBase(BaseModel):

    user_id: int = Field(
        gt=0
    )

    age: int = Field(
        ge=18,
        le=100
    )

    preferred_min_price: float = Field(
        ge=0
    )

    preferred_max_price: float = Field(
        ge=0
    )

    preferred_categories: str = Field(
        min_length=1,
        max_length=500
    )

    preferred_rating: float = Field(
        ge=1,
        le=5
    )


class UserProfileCreate(UserProfileBase):
    pass


class UserProfileUpdate(BaseModel):

    age: int | None = Field(
        default=None,
        ge=18,
        le=100
    )

    preferred_min_price: float | None = Field(
        default=None,
        ge=0
    )

    preferred_max_price: float | None = Field(
        default=None,
        ge=0
    )

    preferred_categories: str | None = Field(
        default=None,
        min_length=1,
        max_length=500
    )

    preferred_rating: float | None = Field(
        default=None,
        ge=1,
        le=5
    )


class UserProfileResponse(UserProfileBase):

    id: int

    model_config = ConfigDict(
        from_attributes=True
    )