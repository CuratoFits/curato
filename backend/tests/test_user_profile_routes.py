from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.dependencies import get_user_profile_service
from app.api.user_profile_routes import router


class FakeProfile:
    id = 1
    user_id = 10
    age = 25
    preferred_min_price = 1000
    preferred_max_price = 3000
    preferred_categories = "DRESSES"
    preferred_rating = 4.5


class FakeService:
    def __init__(self):
        self.profile = FakeProfile()

    def get_profiles(self, skip=0, limit=20):
        return [self.profile]

    def get_profile(self, profile_id):
        if profile_id == 1:
            return self.profile
        return None

    def get_profile_by_user_id(self, user_id):
        if user_id == 10:
            return self.profile
        return None

    def create_profile(self, profile):
        return self.profile

    def update_profile(self, profile_id, profile):
        if profile_id == 1:
            return self.profile
        return None

    def delete_profile(self, profile_id):
        return profile_id == 1


def create_client():
    app = FastAPI()

    app.include_router(
        router,
        prefix="/api",
    )

    app.dependency_overrides[
        get_user_profile_service
    ] = lambda: FakeService()

    return TestClient(app)


def test_get_profiles():
    client = create_client()

    response = client.get(
        "/api/user-profiles"
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


def test_get_profile():
    client = create_client()

    response = client.get(
        "/api/user-profiles/1"
    )

    assert response.status_code == 200
    assert response.json()["user_id"] == 10


def test_get_profile_not_found():
    client = create_client()

    response = client.get(
        "/api/user-profiles/999"
    )

    assert response.status_code == 404


def test_get_profile_by_user_id():
    client = create_client()

    response = client.get(
        "/api/user-profiles/user/10"
    )

    assert response.status_code == 200
    assert response.json()["user_id"] == 10


def test_create_profile():
    client = create_client()

    response = client.post(
        "/api/user-profiles",
        json={
            "user_id": 10,
            "age": 25,
            "preferred_min_price": 1000,
            "preferred_max_price": 3000,
            "preferred_categories": "DRESSES",
            "preferred_rating": 4.5,
        },
    )

    assert response.status_code == 201


def test_update_profile():
    client = create_client()

    response = client.patch(
        "/api/user-profiles/1",
        json={"age": 30},
    )

    assert response.status_code == 200


def test_update_profile_not_found():
    client = create_client()

    response = client.patch(
        "/api/user-profiles/999",
        json={"age": 30},
    )

    assert response.status_code == 404


def test_delete_profile():
    client = create_client()

    response = client.delete(
        "/api/user-profiles/1"
    )

    assert response.status_code == 200


def test_delete_profile_not_found():
    client = create_client()

    response = client.delete(
        "/api/user-profiles/999"
    )

    assert response.status_code == 404
