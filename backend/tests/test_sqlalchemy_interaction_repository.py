from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.db.base import Base
from app.models.interaction import InteractionEvent
from app.repository.implementations.sqlalchemy_interaction_repository import SQLAlchemyInteractionRepository
from app.schemas.interaction import InteractionEventCreate, InteractionEventUpdate

def db_engine():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine, tables=[InteractionEvent.__table__])
    return engine

def payload(user_id=1, product_id=1207):
    return InteractionEventCreate(
        user_id=user_id, product_id=product_id, event_type="view",
        session_id="session_123", time_spent_seconds=10.5,
        scroll_depth=50, source="search", quantity=1,
        timestamp=datetime(2026, 1, 9, 14, 58, 33),
    )

def test_create_and_get_by_id():
    engine = db_engine()
    with Session(engine) as db:
        repo = SQLAlchemyInteractionRepository(db)
        event = repo.create(payload())
        result = repo.get_by_id(event.event_id)
        assert result is not None
        assert result.event_id == event.event_id
    engine.dispose()

def test_get_by_user_id():
    engine = db_engine()
    with Session(engine) as db:
        repo = SQLAlchemyInteractionRepository(db)
        repo.create(payload(user_id=1))
        repo.create(payload(user_id=2))
        assert len(repo.get_by_user_id(1)) == 1
    engine.dispose()

def test_get_by_product_id():
    engine = db_engine()
    with Session(engine) as db:
        repo = SQLAlchemyInteractionRepository(db)
        repo.create(payload(product_id=1207))
        repo.create(payload(product_id=2000))
        assert len(repo.get_by_product_id(1207)) == 1
    engine.dispose()

def test_update():
    engine = db_engine()
    with Session(engine) as db:
        repo = SQLAlchemyInteractionRepository(db)
        event = repo.create(payload())
        result = repo.update(event.event_id, InteractionEventUpdate(event_type="purchase", quantity=2))
        assert result.event_type == "purchase"
        assert result.quantity == 2
    engine.dispose()

def test_update_missing():
    engine = db_engine()
    with Session(engine) as db:
        repo = SQLAlchemyInteractionRepository(db)
        assert repo.update(99999, InteractionEventUpdate(event_type="purchase")) is None
    engine.dispose()

def test_delete():
    engine = db_engine()
    with Session(engine) as db:
        repo = SQLAlchemyInteractionRepository(db)
        event = repo.create(payload())
        assert repo.delete(event.event_id) is True
        assert repo.get_by_id(event.event_id) is None
    engine.dispose()

def test_delete_missing():
    engine = db_engine()
    with Session(engine) as db:
        repo = SQLAlchemyInteractionRepository(db)
        assert repo.delete(99999) is False
    engine.dispose()
