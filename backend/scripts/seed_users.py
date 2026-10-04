from pathlib import Path

import pandas as pd
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert

from app.connections.connection import SessionLocal
from app.models.user import UserProfile

BASE_DIR = Path(__file__).resolve().parents[1]
CSV_PATH = BASE_DIR / "data" / "raw" / "users.csv"
BATCH_SIZE = 500

COLUMNS = [
    "user_id", "age", "gender", "city", "state", "country",
    "preferred_min_price", "preferred_max_price", "preferred_categories",
    "preferred_rating", "preferred_brands", "preferred_colors",
    "preferred_sizes", "preferred_materials", "preferred_styles",
    "preferred_occasions",
]


def seed_users():
    print(f"Reading users from: {CSV_PATH}")
    df = pd.read_csv(CSV_PATH)
    print(f"Users found in CSV: {len(df)}")

    missing = [c for c in COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in users.csv: {missing}")

    df = df[COLUMNS].astype(object).where(pd.notna(df[COLUMNS]), None)
    records = df.to_dict(orient="records")
    for r in records:
        r["user_id"] = int(r["user_id"])
        r["age"] = int(r["age"])

    db = SessionLocal()
    try:
        for start in range(0, len(records), BATCH_SIZE):
            batch = records[start:start + BATCH_SIZE]
            stmt = insert(UserProfile).values(batch)
            stmt = stmt.on_conflict_do_nothing(index_elements=["user_id"])
            db.execute(stmt)
            db.commit()
            print(f"Processed: {min(start + BATCH_SIZE, len(records))}/{len(records)}")

        count = db.execute(text("SELECT COUNT(*) FROM user_profiles")).scalar()
        print(f"\nUsers currently in Supabase: {count}")
    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_users()