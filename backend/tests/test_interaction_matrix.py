import pandas as pd

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent

MATRIX_PATH = (
    BASE_DIR
    / "data"
    / "processed"
    / "user_item_interactions.csv"
)


def test_interaction_matrix_exists():
    assert MATRIX_PATH.exists()


def test_interaction_matrix_columns():

    df = pd.read_csv(MATRIX_PATH)

    expected_columns = {
        "user_id",
        "product_id",
        "interaction_score",
    }

    assert expected_columns.issubset(
        set(df.columns)
    )


def test_interaction_matrix_is_not_empty():

    df = pd.read_csv(MATRIX_PATH)

    assert len(df) > 0


def test_user_ids_are_positive():

    df = pd.read_csv(MATRIX_PATH)

    assert (df["user_id"] > 0).all()


def test_product_ids_are_positive():

    df = pd.read_csv(MATRIX_PATH)

    assert (df["product_id"] > 0).all()


def test_user_product_pairs_are_unique():

    df = pd.read_csv(MATRIX_PATH)

    assert not df.duplicated(
        subset=["user_id", "product_id"]
    ).any()


def test_interaction_scores_exist():

    df = pd.read_csv(MATRIX_PATH)

    assert df["interaction_score"].notna().all()


def test_users_match_expected_dataset():

    df = pd.read_csv(MATRIX_PATH)

    assert df["user_id"].nunique() == 10000


def test_products_match_expected_dataset():

    df = pd.read_csv(MATRIX_PATH)

    assert df["product_id"].nunique() == 2321