from datetime import datetime
from unittest.mock import Mock
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.api.dependencies import get_interaction_service
from app.api.interaction_routes import router
from app.schemas.interaction import InteractionEventResponse

def event():
    return InteractionEventResponse(
        event_id=1, user_id=1, product_id=1207, event_type="view",
        session_id="session_123", time_spent_seconds=33.94,
        scroll_depth=46, source="search", quantity=1,
        timestamp=datetime(2026, 1, 9, 14, 58, 33),
    )

def client_for(service):
    app = FastAPI()
    app.include_router(router, prefix="/api")
    app.dependency_overrides[get_interaction_service] = lambda: service
    return TestClient(app)

def test_get_interactions():
    s = Mock()
    s.get_interactions.return_value = [event()]
    r = client_for(s).get("/api/interactions")
    assert r.status_code == 200
    assert len(r.json()) == 1

def test_get_interaction():
    s = Mock()
    s.get_interaction.return_value = event()
    r = client_for(s).get("/api/interactions/1")
    assert r.status_code == 200
    assert r.json()["event_id"] == 1

def test_get_not_found():
    s = Mock()
    s.get_interaction.return_value = None
    assert client_for(s).get("/api/interactions/999").status_code == 404

def test_get_user_interactions():
    s = Mock()
    s.get_user_interactions.return_value = [event()]
    r = client_for(s).get("/api/interactions/user/1")
    assert r.status_code == 200

def test_get_product_interactions():
    s = Mock()
    s.get_product_interactions.return_value = [event()]
    r = client_for(s).get("/api/interactions/product/1207")
    assert r.status_code == 200

def test_create_interaction():
    s = Mock()
    s.create_interaction.return_value = event()
    payload = {
        "user_id": 1, "product_id": 1207, "event_type": "view",
        "session_id": "session_123", "time_spent_seconds": 33.94,
        "scroll_depth": 46, "source": "search", "quantity": 1,
        "timestamp": "2026-01-09T14:58:33",
    }
    r = client_for(s).post("/api/interactions", json=payload)
    assert r.status_code == 201

def test_invalid_event_type():
    s = Mock()
    payload = {
        "user_id": 1, "product_id": 1207, "event_type": "watched",
        "session_id": "session_123", "time_spent_seconds": 33.94,
        "scroll_depth": 46, "source": "search", "quantity": 1,
        "timestamp": "2026-01-09T14:58:33",
    }
    assert client_for(s).post("/api/interactions", json=payload).status_code == 422

def test_update():
    s = Mock()
    s.update_interaction.return_value = event()
    r = client_for(s).patch("/api/interactions/1", json={"event_type": "purchase"})
    assert r.status_code == 200

def test_update_not_found():
    s = Mock()
    s.update_interaction.return_value = None
    assert client_for(s).patch("/api/interactions/999", json={"event_type": "purchase"}).status_code == 404

def test_delete():
    s = Mock()
    s.delete_interaction.return_value = True
    assert client_for(s).delete("/api/interactions/1").status_code == 200

def test_delete_not_found():
    s = Mock()
    s.delete_interaction.return_value = False
    assert client_for(s).delete("/api/interactions/999").status_code == 404
