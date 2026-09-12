import pytest
from pydantic import ValidationError

from app.schemas.user import (
    UserProfileCreate,
    UserProfileResponse,
    UserProfileUpdate,
)


def valid_profile():
    return {
        "user_id": 1,
        "age": 25,
        "preferred_min_price": 1000,
        "preferred_max_price": 3000,
        "preferred_categories": "DRESSES,TOPS",
        "preferred_rating": 4.2,
    }


def test_user_profile_create_schema():
    profile = UserProfileCreate(**valid_profile())

    assert profile.user_id == 1
    assert profile.age == 25
    assert profile.preferred_min_price == 1000
    assert profile.preferred_max_price == 3000
    assert profile.preferred_rating == 4.2


def test_user_profile_age_validation():
    data = valid_profile()
    data["age"] = 10

    with pytest.raises(ValidationError):
        UserProfileCreate(**data)


def test_user_profile_rating_validation():
    data = valid_profile()
    data["preferred_rating"] = 6

    with pytest.raises(ValidationError):
        UserProfileCreate(**data)


def test_user_profile_price_validation():
    data = valid_profile()
    data["preferred_min_price"] = -100

    with pytest.raises(ValidationError):
        UserProfileCreate(**data)


def test_user_profile_update_is_partial():
    profile = UserProfileUpdate(age=30)

    assert profile.age == 30
    assert profile.preferred_rating is None


def test_user_profile_response_from_attributes():
    class FakeProfile:
        id = 1
        user_id = 10
        age = 25
        preferred_min_price = 1000
        preferred_max_price = 3000
        preferred_categories = "DRESSES"
        preferred_rating = 4.5

    response = UserProfileResponse.model_validate(
        FakeProfile(),
        from_attributes=True,
    )

    assert response.id == 1
    assert response.user_id == 10
