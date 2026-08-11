from sqlalchemy import inspect

from app.models.user import UserProfile


def test_user_profile_table_name():
    assert UserProfile.__tablename__ == "user_profiles"


def test_user_profile_columns():
    mapper = inspect(UserProfile)

    columns = {column.key for column in mapper.columns}

    expected = {
        "id",
        "user_id",
        "age",
        "preferred_min_price",
        "preferred_max_price",
        "preferred_categories",
        "preferred_rating",
    }

    assert expected.issubset(columns)


def test_user_profile_primary_key():
    mapper = inspect(UserProfile)

    primary_keys = {
        column.key for column in mapper.primary_key
    }

    assert primary_keys == {"id"}


def test_user_id_is_unique():
    mapper = inspect(UserProfile)

    user_id_column = mapper.columns["user_id"]

    assert user_id_column.unique is True
