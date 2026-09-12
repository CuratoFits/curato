from datetime import datetime
import pytest
from pydantic import ValidationError
from app.schemas.interaction import InteractionEventCreate, InteractionEventUpdate

def payload():
    return {
        "user_id": 1, "product_id": 1207, "event_type": "view",
        "session_id": "session_123", "time_spent_seconds": 33.94,
        "scroll_depth": 46, "source": "search", "quantity": 1,
        "timestamp": datetime(2026, 1, 9, 14, 58, 33),
    }

def test_create_schema():
    x = InteractionEventCreate(**payload())
    assert x.user_id == 1
    assert x.event_type == "view"

@pytest.mark.parametrize("event_type", [
    "view", "click", "wishlist", "add_to_cart", "purchase", "not_interested"
])
def test_valid_event_types(event_type):
    p = payload()
    p["event_type"] = event_type
    assert InteractionEventCreate(**p).event_type == event_type

def test_invalid_event_type():
    p = payload()
    p["event_type"] = "watched"
    with pytest.raises(ValidationError):
        InteractionEventCreate(**p)

@pytest.mark.parametrize("source", [
    "category", "homepage", "product_page", "recommendation", "search"
])
def test_valid_sources(source):
    p = payload()
    p["source"] = source
    assert InteractionEventCreate(**p).source == source

def test_invalid_source():
    p = payload()
    p["source"] = "random_source"
    with pytest.raises(ValidationError):
        InteractionEventCreate(**p)

def test_invalid_scroll_depth():
    p = payload()
    p["scroll_depth"] = 101
    with pytest.raises(ValidationError):
        InteractionEventCreate(**p)

def test_update_is_partial():
    x = InteractionEventUpdate(event_type="purchase")
    assert x.event_type == "purchase"
    assert x.quantity is None
