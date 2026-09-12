import inspect

from app.repository.interfaces.user_profile_repository import (
    UserProfileRepository,
)


def test_user_profile_repository_is_abstract():
    assert inspect.isabstract(UserProfileRepository)


def test_repository_has_required_methods():
    required_methods = {
        "get_all",
        "get_by_id",
        "get_by_user_id",
        "create",
        "update",
        "delete",
    }

    for method in required_methods:
        assert hasattr(UserProfileRepository, method)
