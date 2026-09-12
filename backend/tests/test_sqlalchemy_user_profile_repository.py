from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.db.base import Base
from app.models.user import UserProfile
from app.repository.implementations.sqlalchemy_user_profile_repository import (
    SQLAlchemyUserProfileRepository,
)
from app.schemas.user import (
    UserProfileCreate,
    UserProfileUpdate,
)


def create_test_database():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)

    return Session()


def create_profile():
    return UserProfileCreate(
        user_id=1,
        age=25,
        preferred_min_price=1000,
        preferred_max_price=3000,
        preferred_categories="DRESSES",
        preferred_rating=4.5,
    )


def test_create():
    db = create_test_database()
    repository = SQLAlchemyUserProfileRepository(db)

    result = repository.create(create_profile())

    assert result.id is not None
    assert result.user_id == 1

    db.close()


def test_get_by_id():
    db = create_test_database()
    repository = SQLAlchemyUserProfileRepository(db)

    created = repository.create(create_profile())
    result = repository.get_by_id(created.id)

    assert result is not None
    assert result.id == created.id

    db.close()


def test_get_by_user_id():
    db = create_test_database()
    repository = SQLAlchemyUserProfileRepository(db)

    repository.create(create_profile())
    result = repository.get_by_user_id(1)

    assert result is not None
    assert result.user_id == 1

    db.close()


def test_get_missing():
    db = create_test_database()
    repository = SQLAlchemyUserProfileRepository(db)

    result = repository.get_by_id(999)

    assert result is None

    db.close()


def test_update():
    db = create_test_database()
    repository = SQLAlchemyUserProfileRepository(db)

    created = repository.create(create_profile())

    updated = repository.update(
        created.id,
        UserProfileUpdate(age=30),
    )

    assert updated is not None
    assert updated.age == 30

    db.close()


def test_update_missing():
    db = create_test_database()
    repository = SQLAlchemyUserProfileRepository(db)

    result = repository.update(
        999,
        UserProfileUpdate(age=30),
    )

    assert result is None

    db.close()


def test_delete():
    db = create_test_database()
    repository = SQLAlchemyUserProfileRepository(db)

    created = repository.create(create_profile())
    result = repository.delete(created.id)

    assert result is True
    assert repository.get_by_id(created.id) is None

    db.close()


def test_delete_missing():
    db = create_test_database()
    repository = SQLAlchemyUserProfileRepository(db)

    result = repository.delete(999)

    assert result is False

    db.close()
