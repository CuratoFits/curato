from pathlib import Path

import pandas as pd
from sqlalchemy import text

from app.connections.connection import SessionLocal
from app.models.interaction import InteractionEvent

BASE_DIR = Path(__file__).resolve().parents[1]
CSV_PATH = BASE_DIR / "data" / "raw" / "interaction_events.csv"
CHUNK_SIZE = 10_000
TOTAL_ROWS = 1_000_000


def seed_interactions():
    print(f"Reading interactions from: {CSV_PATH}")

    if not CSV_PATH.exists():
        raise FileNotFoundError(f"Interaction CSV not found: {CSV_PATH}")

    db = SessionLocal()
    total = 0
    try:
        for n, df in enumerate(pd.read_csv(CSV_PATH, chunksize=CHUNK_SIZE), start=1):
            df["timestamp"] = pd.to_datetime(df["timestamp"])
            records = df.to_dict(orient="records")
            for r in records:
                r["timestamp"] = r["timestamp"].to_pydatetime()

            db.bulk_insert_mappings(InteractionEvent, records)
            db.commit()
            total += len(records)
            print(f"Processed: {total:,}/{TOTAL_ROWS:,} (chunk {n})")

        # keep the event_id sequence ahead of the imported ids
        db.execute(text(
            "SELECT setval(pg_get_serial_sequence('interaction_events','event_id'),"
            " COALESCE((SELECT MAX(event_id) FROM interaction_events),1), true)"
        ))
        db.commit()

        count = db.execute(text("SELECT COUNT(*) FROM interaction_events")).scalar()
        print("\nImport completed successfully.")
        print(f"Interactions currently in Supabase: {count:,}")
    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_interactions()