from datetime import datetime
from unittest.mock import Mock
from app.schemas.interaction import InteractionEventCreate, InteractionEventUpdate
from app.service.interaction_service import InteractionService

def payload():
    return InteractionEventCreate(
        user_id=1, product_id=1207, event_type="view",
        session_id="session_123", time_spent_seconds=10.5,
        scroll_depth=50, source="search", quantity=1,
        timestamp=datetime(2026, 1, 9, 14, 58, 33),
    )

def test_get_interactions():
    repo = Mock()
    repo.get_all.return_value = ["a"]
    result = InteractionService(repo).get_interactions(5, 10)
    repo.get_all.assert_called_once_with(skip=5, limit=10)
    assert result == ["a"]

def test_get_interaction():
    repo = Mock()
    repo.get_by_id.return_value = "event"
    assert InteractionService(repo).get_interaction(1) == "event"
    repo.get_by_id.assert_called_once_with(1)

def test_get_user_interactions():
    repo = Mock()
    repo.get_by_user_id.return_value = ["event"]
    result = InteractionService(repo).get_user_interactions(1, 0, 20)
    repo.get_by_user_id.assert_called_once_with(user_id=1, skip=0, limit=20)
    assert result == ["event"]

def test_get_product_interactions():
    repo = Mock()
    repo.get_by_product_id.return_value = ["event"]
    result = InteractionService(repo).get_product_interactions(1207, 0, 20)
    repo.get_by_product_id.assert_called_once_with(product_id=1207, skip=0, limit=20)
    assert result == ["event"]

def test_create_interaction():
    repo = Mock()
    repo.create.return_value = "created"
    p = payload()
    assert InteractionService(repo).create_interaction(p) == "created"
    repo.create.assert_called_once_with(p)

def test_update_interaction():
    repo = Mock()
    repo.update.return_value = "updated"
    p = InteractionEventUpdate(event_type="purchase")
    assert InteractionService(repo).update_interaction(1, p) == "updated"
    repo.update.assert_called_once_with(1, p)

def test_delete_interaction():
    repo = Mock()
    repo.delete.return_value = True
    assert InteractionService(repo).delete_interaction(1) is True
    repo.delete.assert_called_once_with(1)
