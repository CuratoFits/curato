from pathlib import Path

import pandas as pd


# ============================================================
# Paths
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

PRODUCTS_PATH = RAW_DIR / "products.csv"
USERS_PATH = RAW_DIR / "users.csv"
INTERACTIONS_PATH = RAW_DIR / "interaction_events.csv"


# ============================================================
# Create processed directory
# ============================================================

PROCESSED_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# ============================================================
# Product preprocessing
# ============================================================

def preprocess_products():

    print("Processing products...")

    df = pd.read_csv(PRODUCTS_PATH)

    # Remove completely empty rows
    df = df.dropna(how="all")

    # Remove duplicate product IDs
    df = df.drop_duplicates(
        subset=["product_id"],
        keep="first"
    )

    # Clean text fields
    text_columns = [
        "product_name",
        "category",
        "description",
        "image_url",
        "product_url",
        "gender",
    ]

    for column in text_columns:

        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
        )

    # Convert numeric fields
    df["product_id"] = pd.to_numeric(
        df["product_id"],
        errors="coerce"
    ).astype("Int64")

    df["price"] = pd.to_numeric(
        df["price"],
        errors="coerce"
    )

    df["rating"] = pd.to_numeric(
        df["rating"],
        errors="coerce"
    )

    # Remove products without required fields
    df = df.dropna(
        subset=[
            "product_id",
            "product_name",
            "product_url",
        ]
    )

    # Keep ratings in valid range
    df.loc[
        ~df["rating"].between(1, 5),
        "rating"
    ] = pd.NA

    output_path = (
        PROCESSED_DIR /
        "products_clean.csv"
    )

    df.to_csv(
        output_path,
        index=False
    )

    print(
        f"Products processed: {len(df):,}"
    )

    return df


# ============================================================
# User preprocessing
# ============================================================

def preprocess_users():

    print("Processing users...")

    df = pd.read_csv(USERS_PATH)

    # Remove empty rows
    df = df.dropna(how="all")

    # Remove duplicate users
    df = df.drop_duplicates(
        subset=["user_id"],
        keep="first"
    )

    # Convert numeric fields
    df["user_id"] = pd.to_numeric(
        df["user_id"],
        errors="coerce"
    ).astype("Int64")

    df["age"] = pd.to_numeric(
        df["age"],
        errors="coerce"
    ).astype("Int64")

    df["preferred_min_price"] = pd.to_numeric(
        df["preferred_min_price"],
        errors="coerce"
    )

    df["preferred_max_price"] = pd.to_numeric(
        df["preferred_max_price"],
        errors="coerce"
    )

    df["preferred_rating"] = pd.to_numeric(
        df["preferred_rating"],
        errors="coerce"
    )

    # Clean category strings
    df["preferred_categories"] = (
        df["preferred_categories"]
        .astype("string")
        .str.strip()
    )

    # Remove users missing required fields
    df = df.dropna(
        subset=[
            "user_id",
            "age",
            "preferred_min_price",
            "preferred_max_price",
            "preferred_categories",
            "preferred_rating",
        ]
    )

    # Ensure min <= max
    df = df[
        df["preferred_min_price"]
        <= df["preferred_max_price"]
    ]

    # Valid age
    df = df[
        df["age"].between(18, 100)
    ]

    # Valid rating preference
    df = df[
        df["preferred_rating"].between(1, 5)
    ]

    output_path = (
        PROCESSED_DIR /
        "users_clean.csv"
    )

    df.to_csv(
        output_path,
        index=False
    )

    print(
        f"Users processed: {len(df):,}"
    )

    return df


# ============================================================
# Interaction preprocessing
# ============================================================

def preprocess_interactions(
    valid_user_ids,
    valid_product_ids,
):

    print("Processing interactions...")
    print("This may take a little while...")

    df = pd.read_csv(
        INTERACTIONS_PATH
    )

    # Remove completely empty rows
    df = df.dropna(how="all")

    # Remove duplicate event IDs
    df = df.drop_duplicates(
        subset=["event_id"],
        keep="first"
    )

    # --------------------------------------------------------
    # Numeric fields
    # --------------------------------------------------------

    numeric_columns = [
        "event_id",
        "user_id",
        "product_id",
        "time_spent_seconds",
        "scroll_depth",
        "quantity",
    ]

    for column in numeric_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # --------------------------------------------------------
    # Text fields
    # --------------------------------------------------------

    text_columns = [
        "event_type",
        "session_id",
        "source",
    ]

    for column in text_columns:

        df[column] = (
            df[column]
            .astype("string")
            .str.strip()
        )

    # --------------------------------------------------------
    # Timestamp
    # --------------------------------------------------------

    df["timestamp"] = pd.to_datetime(
        df["timestamp"],
        errors="coerce"
    )

    # --------------------------------------------------------
    # Remove invalid IDs
    # --------------------------------------------------------

    df = df[
        df["user_id"].isin(
            valid_user_ids
        )
    ]

    df = df[
        df["product_id"].isin(
            valid_product_ids
        )
    ]

    # --------------------------------------------------------
    # Valid event types
    # --------------------------------------------------------

    valid_events = {
        "view",
        "click",
        "wishlist",
        "add_to_cart",
        "purchase",
        "not_interested",
    }

    df = df[
        df["event_type"].isin(
            valid_events
        )
    ]

    # --------------------------------------------------------
    # Valid sources
    # --------------------------------------------------------

    valid_sources = {
        "homepage",
        "search",
        "category",
        "product_page",
        "recommendation",
    }

    df = df[
        df["source"].isin(
            valid_sources
        )
    ]

    # --------------------------------------------------------
    # Valid numerical values
    # --------------------------------------------------------

    df = df[
        df["time_spent_seconds"] >= 0
    ]

    df = df[
        df["scroll_depth"].between(
            0,
            100
        )
    ]

    df = df[
        df["quantity"] >= 1
    ]

    # --------------------------------------------------------
    # Remove rows with missing required values
    # --------------------------------------------------------

    df = df.dropna(
        subset=[
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
        ]
    )

    # --------------------------------------------------------
    # Convert IDs to integers
    # --------------------------------------------------------

    df["event_id"] = (
        df["event_id"]
        .astype("int64")
    )

    df["user_id"] = (
        df["user_id"]
        .astype("int64")
    )

    df["product_id"] = (
        df["product_id"]
        .astype("int64")
    )

    df["quantity"] = (
        df["quantity"]
        .astype("int64")
    )

    # --------------------------------------------------------
    # Sort events chronologically
    # --------------------------------------------------------

    df = df.sort_values(
        by=[
            "user_id",
            "timestamp",
        ]
    ).reset_index(
        drop=True
    )

    output_path = (
        PROCESSED_DIR /
        "interaction_events_clean.csv"
    )

    df.to_csv(
        output_path,
        index=False
    )

    print(
        f"Interactions processed: {len(df):,}"
    )

    return df


# ============================================================
# Main
# ============================================================

def main():

    print("=" * 60)
    print("RECOMMENDER DATA PREPROCESSING")
    print("=" * 60)

    # Products
    products = preprocess_products()

    # Users
    users = preprocess_users()

    # IDs used for interaction validation
    valid_user_ids = set(
        users["user_id"].astype(int)
    )

    valid_product_ids = set(
        products["product_id"].astype(int)
    )

    # Interactions
    interactions = preprocess_interactions(
        valid_user_ids,
        valid_product_ids,
    )

    # --------------------------------------------------------
    # Summary
    # --------------------------------------------------------

    print("\n" + "=" * 60)
    print("PREPROCESSING COMPLETED")
    print("=" * 60)

    print(
        f"Products : {len(products):,}"
    )

    print(
        f"Users    : {len(users):,}"
    )

    print(
        f"Events   : {len(interactions):,}"
    )

    print(
        f"\nProcessed files saved to:\n"
        f"{PROCESSED_DIR}"
    )


if __name__ == "__main__":
    main()