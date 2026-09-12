import inspect
from app.repository.interfaces.interaction_repository import InteractionRepository

def test_interaction_repository_is_abstract():
    assert inspect.isabstract(InteractionRepository)

def test_required_methods_are_abstract():
    methods = [
        "get_all", "get_by_id", "get_by_user_id", "get_by_product_id",
        "create", "update", "delete"
    ]
    for method in methods:
        assert hasattr(InteractionRepository, method)
        assert getattr(InteractionRepository, method).__isabstractmethod__
