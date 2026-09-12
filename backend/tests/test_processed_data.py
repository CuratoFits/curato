from pathlib import Path

import pandas as pd


# ============================================================
# Paths
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

PROCESSED_DIR = BASE_DIR / "data" / "processed"

PRODUCTS_PATH = (
    PROCESSED_DIR / "products_clean.csv"
)

USERS_PATH = (
    PROCESSED_DIR / "users_clean.csv"
)

INTERACTIONS_PATH = (
    PROCESSED_DIR / "interaction_events_clean.csv"
)


# ============================================================
# Products
# ============================================================

def test_processed_products_file_exists():
    assert PRODUCTS_PATH.exists()


def test_processed_products_count():
    df = pd.read_csv(PRODUCTS_PATH)

    assert len(df) == 2321


def test_processed_product_ids_unique():
    df = pd.read_csv(PRODUCTS_PATH)

    assert df["product_id"].is_unique


def test_processed_product_names_not_missing():
    df = pd.read_csv(PRODUCTS_PATH)

    assert df["product_name"].notna().all()


def test_processed_product_urls_unique():
    df = pd.read_csv(PRODUCTS_PATH)

    assert df["product_url"].notna().all()
    assert df["product_url"].is_unique


def test_processed_product_ratings_valid():
    df = pd.read_csv(PRODUCTS_PATH)

    assert df["rating"].dropna().between(1, 5).all()


# ============================================================
# Users
# ============================================================

def test_processed_users_file_exists():
    assert USERS_PATH.exists()


def test_processed_users_count():
    df = pd.read_csv(USERS_PATH)

    assert len(df) == 10000


def test_processed_user_ids_unique():
    df = pd.read_csv(USERS_PATH)

    assert df["user_id"].is_unique


def test_processed_users_age_valid():
    df = pd.read_csv(USERS_PATH)

    assert df["age"].between(18, 100).all()


def test_processed_users_price_range_valid():
    df = pd.read_csv(USERS_PATH)

    assert (
        df["preferred_min_price"]
        <= df["preferred_max_price"]
    ).all()


def test_processed_user_rating_valid():
    df = pd.read_csv(USERS_PATH)

    assert (
        df["preferred_rating"]
        .between(1, 5)
        .all()
    )


def test_processed_user_categories_not_missing():
    df = pd.read_csv(USERS_PATH)

    assert (
        df["preferred_categories"]
        .notna()
        .all()
    )


# ============================================================
# Interactions
# ============================================================

def test_processed_interactions_file_exists():
    assert INTERACTIONS_PATH.exists()


def test_processed_interactions_count():
    df = pd.read_csv(INTERACTIONS_PATH)

    assert len(df) == 1_000_000


def test_processed_event_ids_unique():
    df = pd.read_csv(INTERACTIONS_PATH)

    assert df["event_id"].is_unique


def test_processed_interaction_event_types():
    df = pd.read_csv(INTERACTIONS_PATH)

    valid_events = {
        "view",
        "click",
        "wishlist",
        "add_to_cart",
        "purchase",
        "not_interested",
    }

    assert set(df["event_type"].unique()) <= valid_events


def test_processed_interaction_sources():
    df = pd.read_csv(INTERACTIONS_PATH)

    valid_sources = {
        "homepage",
        "search",
        "category",
        "product_page",
        "recommendation",
    }

    assert set(df["source"].unique()) <= valid_sources


def test_processed_interaction_time_valid():
    df = pd.read_csv(INTERACTIONS_PATH)

    assert (
        df["time_spent_seconds"] >= 0
    ).all()


def test_processed_interaction_scroll_valid():
    df = pd.read_csv(INTERACTIONS_PATH)

    assert (
        df["scroll_depth"]
        .between(0, 100)
        .all()
    )


def test_processed_interaction_quantity_valid():
    df = pd.read_csv(INTERACTIONS_PATH)

    assert (
        df["quantity"] >= 1
    ).all()


def test_processed_interaction_timestamps_valid():
    df = pd.read_csv(INTERACTIONS_PATH)

    timestamps = pd.to_datetime(
        df["timestamp"],
        errors="coerce"
    )

    assert timestamps.notna().all()


# ============================================================
# Referential integrity
# ============================================================

def test_interaction_user_ids_exist():

    users = pd.read_csv(
        USERS_PATH,
        usecols=["user_id"]
    )

    interactions = pd.read_csv(
        INTERACTIONS_PATH,
        usecols=["user_id"]
    )

    valid_user_ids = set(
        users["user_id"]
    )

    interaction_user_ids = set(
        interactions["user_id"]
    )

    assert interaction_user_ids <= valid_user_ids


def test_interaction_product_ids_exist():

    products = pd.read_csv(
        PRODUCTS_PATH,
        usecols=["product_id"]
    )

    interactions = pd.read_csv(
        INTERACTIONS_PATH,
        usecols=["product_id"]
    )

    valid_product_ids = set(
        products["product_id"]
    )

    interaction_product_ids = set(
        interactions["product_id"]
    )

    assert (
        interaction_product_ids
        <= valid_product_ids
    )