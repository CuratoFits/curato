from pathlib import Path

import pandas as pd
from sqlalchemy import text

from app.connections.connection import SessionLocal


# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

CSV_PATH = (
    BASE_DIR
    / "data"
    / "raw"
    / "interaction_events.csv"
)

CHUNK_SIZE = 10_000


# ---------------------------------------------------------
# VALID VALUES
# ---------------------------------------------------------

REQUIRED_COLUMNS = {
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


VALID_EVENT_TYPES = {
    "view",
    "click",
    "wishlist",
    "add_to_cart",
    "purchase",
    "not_interested",
}


VALID_SOURCES = {
    "category",
    "homepage",
    "product_page",
    "recommendation",
    "search",
}


# ---------------------------------------------------------
# VALIDATE CSV
# ---------------------------------------------------------

def validate_csv():

    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"Interaction CSV not found: {CSV_PATH}"
        )

    header = pd.read_csv(
        CSV_PATH,
        nrows=0,
    )

    actual_columns = set(header.columns)

    missing = REQUIRED_COLUMNS - actual_columns

    if missing:
        raise ValueError(
            f"Missing columns: {sorted(missing)}"
        )


# ---------------------------------------------------------
# SEED INTERACTIONS
# ---------------------------------------------------------

def seed_interactions():

    print(
        f"Reading interactions from: {CSV_PATH}"
    )

    validate_csv()

    db = SessionLocal()

    inserted = 0

    try:

        # Clear existing interaction data.
        # This makes the script safe to rerun during
        # development without creating duplicates.
        db.execute(
            text(
                "TRUNCATE TABLE interaction_events"
            )
        )

        db.commit()

        # Read the 1-million-row CSV in chunks.
        for chunk_number, df in enumerate(
            pd.read_csv(
                CSV_PATH,
                chunksize=CHUNK_SIZE,
            ),
            start=1,
        ):

            # ---------------------------------------------
            # Validate event types
            # ---------------------------------------------

            invalid_events = (
                set(
                    df["event_type"]
                    .dropna()
                    .unique()
                )
                - VALID_EVENT_TYPES
            )

            if invalid_events:
                raise ValueError(
                    f"Invalid event types: "
                    f"{sorted(invalid_events)}"
                )

            # ---------------------------------------------
            # Validate sources
            # ---------------------------------------------

            invalid_sources = (
                set(
                    df["source"]
                    .dropna()
                    .unique()
                )
                - VALID_SOURCES
            )

            if invalid_sources:
                raise ValueError(
                    f"Invalid sources: "
                    f"{sorted(invalid_sources)}"
                )

            # ---------------------------------------------
            # Convert timestamp
            # ---------------------------------------------

            df["timestamp"] = pd.to_datetime(
                df["timestamp"]
            )

            # ---------------------------------------------
            # Convert dataframe to dictionaries
            # ---------------------------------------------

            rows = df.to_dict(
                orient="records"
            )

            # ---------------------------------------------
            # Bulk insert
            # ---------------------------------------------

            db.execute(
                text(
                    """
                    INSERT INTO interaction_events (
                        event_id,
                        user_id,
                        product_id,
                        event_type,
                        session_id,
                        time_spent_seconds,
                        scroll_depth,
                        source,
                        quantity,
                        timestamp
                    )
                    VALUES (
                        :event_id,
                        :user_id,
                        :product_id,
                        :event_type,
                        :session_id,
                        :time_spent_seconds,
                        :scroll_depth,
                        :source,
                        :quantity,
                        :timestamp
                    )
                    """
                ),
                rows,
            )

            db.commit()

            inserted += len(df)

            print(
                f"Processed chunk {chunk_number}: "
                f"{inserted:,} rows"
            )

        print()
        print(
            "Interaction seeding completed."
        )
        print(
            f"Inserted: {inserted:,}"
        )

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()


# ---------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------

if __name__ == "__main__":
    seed_interactions()