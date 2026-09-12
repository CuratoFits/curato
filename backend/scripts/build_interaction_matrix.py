from pathlib import Path

import pandas as pd


# --------------------------------------------------
# PATHS
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

INPUT_PATH = (
    BASE_DIR
    / "data"
    / "raw"
    / "interaction_events.csv"
)

OUTPUT_DIR = (
    BASE_DIR
    / "data"
    / "processed"
)

OUTPUT_PATH = (
    OUTPUT_DIR
    / "user_item_interactions.csv"
)


# --------------------------------------------------
# EVENT WEIGHTS
# --------------------------------------------------

EVENT_WEIGHTS = {
    "view": 1,
    "click": 2,
    "wishlist": 4,
    "add_to_cart": 6,
    "purchase": 10,
    "not_interested": -5,
}


# --------------------------------------------------
# BUILD INTERACTION DATA
# --------------------------------------------------

def build_interaction_matrix():

    print("Reading interaction data...")

    df = pd.read_csv(INPUT_PATH)

    print(
        f"Total raw interactions: {len(df):,}"
    )

    # Convert event type into numerical score
    df["interaction_score"] = (
        df["event_type"].map(EVENT_WEIGHTS)
    )

    # Check for unknown event types
    if df["interaction_score"].isna().any():

        invalid_events = (
            df.loc[
                df["interaction_score"].isna(),
                "event_type"
            ]
            .unique()
            .tolist()
        )

        raise ValueError(
            f"Unknown event types: {invalid_events}"
        )

    # Combine repeated interactions between
    # the same user and product.
    result = (
        df.groupby(
            ["user_id", "product_id"],
            as_index=False
        )["interaction_score"]
        .sum()
    )

    # Create processed directory
    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    # Save result
    result.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print()
    print("Done!")
    print(
        f"Unique user-product pairs: "
        f"{len(result):,}"
    )

    print(
        f"Users: "
        f"{result['user_id'].nunique():,}"
    )

    print(
        f"Products: "
        f"{result['product_id'].nunique():,}"
    )

    print()
    print("First 5 rows:")
    print(result.head())

    print()
    print(
        f"Saved to: {OUTPUT_PATH}"
    )


if __name__ == "__main__":
    build_interaction_matrix()