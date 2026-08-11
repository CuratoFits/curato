from app.models.interaction import InteractionEvent

def test_interaction_table_name():
    assert InteractionEvent.__tablename__ == "interaction_events"

def test_interaction_columns():
    assert set(InteractionEvent.__table__.columns.keys()) == {
        "event_id", "user_id", "product_id", "event_type", "session_id",
        "time_spent_seconds", "scroll_depth", "source", "quantity", "timestamp"
    }

def test_event_id_primary_key():
    assert InteractionEvent.__table__.c.event_id.primary_key is True
