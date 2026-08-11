from pathlib import Path

import pandas as pd


# ============================================================
# Paths
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

RAW_DIR = BASE_DIR / "data" / "raw"

PRODUCTS_PATH = RAW_DIR / "products.csv"
USERS_PATH = RAW_DIR / "users.csv"
INTERACTIONS_PATH = RAW_DIR / "interaction_events.csv"


# ============================================================
# Expected values
# ============================================================

VALID_EVENT_TYPES = {
    "view",
    "click",
    "wishlist",
    "add_to_cart",
    "purchase",
    "not_interested",
}

VALID_SOURCES = {
    "homepage",
    "search",
    "category",
    "product_page",
    "recommendation",
}


# ============================================================
# Product validation
# ============================================================

def validate_products():

    errors = []

    if not PRODUCTS_PATH.exists():
        errors.append(
            f"products.csv not found: {PRODUCTS_PATH}"
        )
        return errors

    df = pd.read_csv(PRODUCTS_PATH)

    print(f"Products: {len(df):,}")

    # Expected number of products
    if len(df) != 2321:
        errors.append(
            f"Expected 2321 products, found {len(df)}"
        )

    # Required columns
    required_columns = {
        "product_id",
        "product_name",
        "category",
        "price",
        "description",
        "image_url",
        "product_url",
        "gender",
        "rating",
    }

    missing = required_columns - set(df.columns)

    if missing:
        errors.append(
            f"Missing product columns: {sorted(missing)}"
        )
        return errors

    # Product IDs
    if df["product_id"].isna().any():
        errors.append(
            "product_id contains NULL values"
        )

    if not df["product_id"].is_unique:
        errors.append(
            "product_id contains duplicates"
        )

    # Product names
    if df["product_name"].isna().any():
        errors.append(
            "product_name contains NULL values"
        )

    # Product URLs
    if df["product_url"].isna().any():
        errors.append(
            "product_url contains NULL values"
        )

    if not df["product_url"].dropna().is_unique:
        errors.append(
            "product_url contains duplicates"
        )

    # Price
    if (df["price"] < 0).any():
        errors.append(
            "price contains negative values"
        )

    # Rating
    invalid_rating = df[
        ~df["rating"].between(1, 5)
    ]

    if len(invalid_rating) > 0:
        errors.append(
            f"{len(invalid_rating)} products have "
            "invalid ratings"
        )

    # Gender
    genders = set(
        df["gender"].dropna().astype(str)
    )

    if genders != {"Women"}:
        errors.append(
            f"Unexpected gender values: {genders}"
        )

    return errors


# ============================================================
# User validation
# ============================================================

def validate_users():

    errors = []

    if not USERS_PATH.exists():
        errors.append(
            f"users.csv not found: {USERS_PATH}"
        )
        return errors

    df = pd.read_csv(USERS_PATH)

    print(f"Users: {len(df):,}")

    # Number of users
    if len(df) != 10000:
        errors.append(
            f"Expected 10000 users, found {len(df)}"
        )

    # Required columns
    required_columns = {
        "user_id",
        "age",
        "preferred_min_price",
        "preferred_max_price",
        "preferred_categories",
        "preferred_rating",
    }

    missing = required_columns - set(df.columns)

    if missing:
        errors.append(
            f"Missing user columns: {sorted(missing)}"
        )
        return errors

    # User IDs
    if df["user_id"].isna().any():
        errors.append(
            "user_id contains NULL values"
        )

    if not df["user_id"].is_unique:
        errors.append(
            "user_id contains duplicates"
        )

    # Age
    invalid_age = df[
        ~df["age"].between(18, 100)
    ]

    if len(invalid_age) > 0:
        errors.append(
            f"{len(invalid_age)} users have invalid ages"
        )

    # Price ranges
    invalid_price = df[
        df["preferred_min_price"]
        > df["preferred_max_price"]
    ]

    if len(invalid_price) > 0:
        errors.append(
            f"{len(invalid_price)} users have invalid "
            "price ranges"
        )

    # Rating preference
    invalid_rating = df[
        ~df["preferred_rating"].between(1, 5)
    ]

    if len(invalid_rating) > 0:
        errors.append(
            f"{len(invalid_rating)} users have invalid "
            "preferred ratings"
        )

    # Categories
    if df["preferred_categories"].isna().any():
        errors.append(
            "preferred_categories contains NULL values"
        )

    return errors


# ============================================================
# Interaction validation
# ============================================================

def validate_interactions():

    errors = []

    if not INTERACTIONS_PATH.exists():
        errors.append(
            f"interaction_events.csv not found: "
            f"{INTERACTIONS_PATH}"
        )
        return errors

    print("Loading interaction_events.csv...")

    df = pd.read_csv(INTERACTIONS_PATH)

    print(f"Interactions: {len(df):,}")

    # Number of interactions
    if len(df) != 1_000_000:
        errors.append(
            f"Expected 1,000,000 interactions, "
            f"found {len(df):,}"
        )

    # Required columns
    required_columns = {
        "event_id",
        "user_id",
        "product_id",
        "event_type",
        "session_id",
        "time_spent_seconds",
        "scroll_depth",
        "source",
        "quantity",
        "timestamp",
    }

    missing = required_columns - set(df.columns)

    if missing:
        errors.append(
            f"Missing interaction columns: {sorted(missing)}"
        )
        return errors

    # Event IDs
    if df["event_id"].isna().any():
        errors.append(
            "event_id contains NULL values"
        )

    if not df["event_id"].is_unique:
        errors.append(
            "event_id contains duplicates"
        )

    # User IDs
    if df["user_id"].isna().any():
        errors.append(
            "Interaction user_id contains NULL values"
        )

    # Product IDs
    if df["product_id"].isna().any():
        errors.append(
            "Interaction product_id contains NULL values"
        )

    # --------------------------------------------------------
    # Check user IDs against users.csv
    # --------------------------------------------------------

    users = pd.read_csv(
        USERS_PATH,
        usecols=["user_id"]
    )

    valid_user_ids = set(
        users["user_id"].astype(int)
    )

    interaction_user_ids = set(
        df["user_id"].astype(int)
    )

    unknown_users = (
        interaction_user_ids
        - valid_user_ids
    )

    if unknown_users:
        errors.append(
            f"Found {len(unknown_users)} unknown user IDs"
        )

    # --------------------------------------------------------
    # Check product IDs against products.csv
    # --------------------------------------------------------

    products = pd.read_csv(
        PRODUCTS_PATH,
        usecols=["product_id"]
    )

    valid_product_ids = set(
        products["product_id"].astype(int)
    )

    interaction_product_ids = set(
        df["product_id"].astype(int)
    )

    unknown_products = (
        interaction_product_ids
        - valid_product_ids
    )

    if unknown_products:
        errors.append(
            f"Found {len(unknown_products)} unknown "
            "product IDs"
        )

    # --------------------------------------------------------
    # Event types
    # --------------------------------------------------------

    actual_events = set(
        df["event_type"]
        .dropna()
        .astype(str)
    )

    invalid_events = (
        actual_events - VALID_EVENT_TYPES
    )

    if invalid_events:
        errors.append(
            f"Invalid event types: {invalid_events}"
        )

    # --------------------------------------------------------
    # Sources
    # --------------------------------------------------------

    actual_sources = set(
        df["source"]
        .dropna()
        .astype(str)
    )

    invalid_sources = (
        actual_sources - VALID_SOURCES
    )

    if invalid_sources:
        errors.append(
            f"Invalid sources: {invalid_sources}"
        )

    # --------------------------------------------------------
    # Time spent
    # --------------------------------------------------------

    if df["time_spent_seconds"].isna().any():
        errors.append(
            "time_spent_seconds contains NULL values"
        )

    if (df["time_spent_seconds"] < 0).any():
        errors.append(
            "time_spent_seconds contains negative values"
        )

    # --------------------------------------------------------
    # Scroll depth
    # --------------------------------------------------------

    invalid_scroll = df[
        ~df["scroll_depth"].between(0, 100)
    ]

    if len(invalid_scroll) > 0:
        errors.append(
            f"{len(invalid_scroll)} invalid scroll_depth values"
        )

    # --------------------------------------------------------
    # Quantity
    # --------------------------------------------------------

    if df["quantity"].isna().any():
        errors.append(
            "quantity contains NULL values"
        )

    if (df["quantity"] < 1).any():
        errors.append(
            "quantity contains values below 1"
        )

    # --------------------------------------------------------
    # Timestamp
    # --------------------------------------------------------

    timestamps = pd.to_datetime(
        df["timestamp"],
        errors="coerce"
    )

    invalid_timestamps = timestamps.isna().sum()

    if invalid_timestamps > 0:
        errors.append(
            f"{invalid_timestamps} invalid timestamps"
        )

    return errors


# ============================================================
# Main
# ============================================================

def main():

    print("=" * 60)
    print("RECOMMENDER DATA VALIDATION")
    print("=" * 60)

    # Validate products
    print("\nPRODUCT DATA")
    print("-" * 60)

    product_errors = validate_products()

    if product_errors:
        for error in product_errors:
            print(f"  ❌ {error}")
    else:
        print("  ✅ Products passed validation")

    # Validate users
    print("\nUSER DATA")
    print("-" * 60)

    user_errors = validate_users()

    if user_errors:
        for error in user_errors:
            print(f"  ❌ {error}")
    else:
        print("  ✅ Users passed validation")

    # Validate interactions
    print("\nINTERACTION DATA")
    print("-" * 60)

    interaction_errors = validate_interactions()

    if interaction_errors:
        for error in interaction_errors:
            print(f"  ❌ {error}")
    else:
        print("  ✅ Interactions passed validation")

    # Final result
    print("\n" + "=" * 60)

    all_errors = (
        product_errors
        + user_errors
        + interaction_errors
    )

    if all_errors:
        print("❌ DATA VALIDATION FAILED")
        print(f"Total errors: {len(all_errors)}")
        print("=" * 60)

        return 1

    print("✅ DATA VALIDATION PASSED")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())