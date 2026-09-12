from pathlib import Path

import pandas as pd
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert

from app.connections.connection import SessionLocal
from app.models.user import UserProfile


BASE_DIR = Path(__file__).resolve().parents[1]
CSV_PATH = BASE_DIR / "data" / "raw" / "users.csv"

BATCH_SIZE = 500


def seed_users():
    print(f"Reading users from: {CSV_PATH}")

    df = pd.read_csv(CSV_PATH)

    print(f"Users found in CSV: {len(df)}")

    records = []

    for _, row in df.iterrows():
        records.append(
            {
                "user_id": int(row["user_id"]),
                "age": int(row["age"]),
                "preferred_min_price": float(row["preferred_min_price"]),
                "preferred_max_price": float(row["preferred_max_price"]),
                "preferred_categories": str(row["preferred_categories"]),
                "preferred_rating": float(row["preferred_rating"]),
            }
        )

    db = SessionLocal()

    try:
        for start in range(0, len(records), BATCH_SIZE):
            batch = records[start:start + BATCH_SIZE]

            stmt = insert(UserProfile).values(batch)

            stmt = stmt.on_conflict_do_nothing(
                index_elements=["user_id"]
            )

            db.execute(stmt)
            db.commit()

            processed = min(start + BATCH_SIZE, len(records))
            print(f"Processed: {processed}/{len(records)}")

        count = db.execute(
            text("SELECT COUNT(*) FROM user_profiles")
        ).scalar()

        print()
        print(f"Users currently in Supabase: {count}")

    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_users()