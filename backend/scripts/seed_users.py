from pathlib import Path

import pandas as pd
from sqlalchemy import select

from app.connections.connection import SessionLocal
from app.models.user import UserProfile


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

CSV_PATH = (
    BASE_DIR
    / "data"
    / "raw"
    / "users.csv"
)


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------

def clean_value(value):

    if pd.isna(value):
        return None

    return value


# ---------------------------------------------------------
# Main seeding function
# ---------------------------------------------------------

def seed_users():

    print(
        f"Reading users from: {CSV_PATH}"
    )

    if not CSV_PATH.exists():

        raise FileNotFoundError(
            f"Users CSV not found: {CSV_PATH}"
        )

    df = pd.read_csv(CSV_PATH)

    print(
        f"Users found in CSV: {len(df)}"
    )

    required_columns = {
        "user_id",
        "age",
        "preferred_min_price",
        "preferred_max_price",
        "preferred_categories",
        "preferred_rating",
    }

    missing_columns = (
        required_columns
        - set(df.columns)
    )

    if missing_columns:

        raise ValueError(
            "Missing columns in users.csv: "
            f"{sorted(missing_columns)}"
        )

    # -----------------------------------------------------
    # Open database
    # -----------------------------------------------------

    db = SessionLocal()

    try:

        # -------------------------------------------------
        # Get all existing user IDs in ONE query
        # -------------------------------------------------

        existing_ids = set(
            db.scalars(
                select(UserProfile.user_id)
            ).all()
        )

        print(
            f"Existing users in database: "
            f"{len(existing_ids)}"
        )

        # -------------------------------------------------
        # Prepare new profiles
        # -------------------------------------------------

        profiles = []

        skipped = 0

        for _, row in df.iterrows():

            user_id = clean_value(
                row["user_id"]
            )

            if user_id is None:

                skipped += 1
                continue

            user_id = int(user_id)

            # Already in database
            if user_id in existing_ids:

                skipped += 1
                continue

            profile = UserProfile(

                user_id=user_id,

                age=int(
                    row["age"]
                ),

                preferred_min_price=float(
                    row["preferred_min_price"]
                ),

                preferred_max_price=float(
                    row["preferred_max_price"]
                ),

                preferred_categories=str(
                    row["preferred_categories"]
                ),

                preferred_rating=float(
                    row["preferred_rating"]
                ),
            )

            profiles.append(profile)

        # -------------------------------------------------
        # Bulk insert
        # -------------------------------------------------

        if profiles:

            db.add_all(profiles)

            db.commit()

        inserted = len(profiles)

        # -------------------------------------------------
        # Results
        # -------------------------------------------------

        print()
        print(
            "User profile seeding completed."
        )

        print(
            f"Inserted: {inserted}"
        )

        print(
            f"Skipped: {skipped}"
        )

        print(
            f"CSV total: {len(df)}"
        )

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------

if __name__ == "__main__":

    seed_users()