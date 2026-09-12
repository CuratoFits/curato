from app.schemas.user import (
    UserProfileCreate,
    UserProfileUpdate,
)
from app.service.user_profile_service import UserProfileService


class FakeUserProfileRepository:
    def __init__(self):
        self.profiles = {}
        self.next_id = 1

    def get_all(self, skip=0, limit=20):
        profiles = list(self.profiles.values())
        return profiles[skip:skip + limit]

    def get_by_id(self, profile_id):
        return self.profiles.get(profile_id)

    def get_by_user_id(self, user_id):
        for profile in self.profiles.values():
            if profile.user_id == user_id:
                return profile
        return None

    def create(self, profile):
        class FakeProfile:
            pass

        result = FakeProfile()
        result.id = self.next_id
        self.next_id += 1
        result.user_id = profile.user_id
        result.age = profile.age
        result.preferred_min_price = profile.preferred_min_price
        result.preferred_max_price = profile.preferred_max_price
        result.preferred_categories = profile.preferred_categories
        result.preferred_rating = profile.preferred_rating

        self.profiles[result.id] = result
        return result

    def update(self, profile_id, profile):
        existing = self.profiles.get(profile_id)

        if existing is None:
            return None

        data = profile.model_dump(exclude_unset=True)

        for key, value in data.items():
            setattr(existing, key, value)

        return existing

    def delete(self, profile_id):
        if profile_id not in self.profiles:
            return False

        del self.profiles[profile_id]
        return True


def create_service():
    repository = FakeUserProfileRepository()
    return UserProfileService(repository)


def test_create_profile():
    service = create_service()

    profile = UserProfileCreate(
        user_id=1,
        age=25,
        preferred_min_price=1000,
        preferred_max_price=3000,
        preferred_categories="DRESSES",
        preferred_rating=4.5,
    )

    result = service.create_profile(profile)

    assert result.user_id == 1
    assert result.age == 25


def test_get_profile():
    service = create_service()

    profile = UserProfileCreate(
        user_id=1,
        age=25,
        preferred_min_price=1000,
        preferred_max_price=3000,
        preferred_categories="DRESSES",
        preferred_rating=4.5,
    )

    created = service.create_profile(profile)
    result = service.get_profile(created.id)

    assert result is not None
    assert result.id == created.id


def test_get_profile_by_user_id():
    service = create_service()

    profile = UserProfileCreate(
        user_id=10,
        age=25,
        preferred_min_price=1000,
        preferred_max_price=3000,
        preferred_categories="DRESSES",
        preferred_rating=4.5,
    )

    service.create_profile(profile)
    result = service.get_profile_by_user_id(10)

    assert result is not None
    assert result.user_id == 10


def test_get_missing_profile():
    service = create_service()

    result = service.get_profile(999)

    assert result is None


def test_update_profile():
    service = create_service()

    profile = UserProfileCreate(
        user_id=1,
        age=25,
        preferred_min_price=1000,
        preferred_max_price=3000,
        preferred_categories="DRESSES",
        preferred_rating=4.5,
    )

    created = service.create_profile(profile)

    updated = service.update_profile(
        created.id,
        UserProfileUpdate(age=30),
    )

    assert updated.age == 30


def test_delete_profile():
    service = create_service()

    profile = UserProfileCreate(
        user_id=1,
        age=25,
        preferred_min_price=1000,
        preferred_max_price=3000,
        preferred_categories="DRESSES",
        preferred_rating=4.5,
    )

    created = service.create_profile(profile)
    result = service.delete_profile(created.id)

    assert result is True
    assert service.get_profile(created.id) is None


def test_invalid_price_range():
    service = create_service()

    profile = UserProfileCreate(
        user_id=1,
        age=25,
        preferred_min_price=5000,
        preferred_max_price=1000,
        preferred_categories="DRESSES",
        preferred_rating=4.5,
    )

    try:
        service.create_profile(profile)
        assert False
    except ValueError as exc:
        assert "Minimum price" in str(exc)
