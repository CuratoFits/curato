from pathlib import Path

import pandas as pd
from sqlalchemy import text

from app.connections.connection import SessionLocal
from app.models.interaction import InteractionEvent


BASE_DIR = Path(__file__).resolve().parents[1]
CSV_PATH = BASE_DIR / "data" / "raw" / "interaction_events.csv"

CHUNK_SIZE = 10_000


def seed_interactions():
    print(f"Reading interactions from: {CSV_PATH}")

    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"Interaction CSV not found: {CSV_PATH}"
        )

    db = SessionLocal()

    total_processed = 0

    try:
        for chunk_number, df in enumerate(
            pd.read_csv(
                CSV_PATH,
                chunksize=CHUNK_SIZE,
            ),
            start=1,
        ):
            records = df.to_dict(orient="records")

            # Convert pandas timestamps to Python datetime
            for record in records:
                record["timestamp"] = pd.to_datetime(
                    record["timestamp"]
                ).to_pydatetime()

            db.bulk_insert_mappings(
                InteractionEvent,
                records,
            )

            db.commit()

            total_processed += len(records)

            print(
                f"Processed: {total_processed:,}/1,000,000 "
                f"(chunk {chunk_number})"
            )

        count = db.execute(
            text("SELECT COUNT(*) FROM interaction_events")
        ).scalar()

        print()
        print("Import completed successfully.")
        print(f"Interactions currently in Supabase: {count:,}")

    except Exception as e:
        db.rollback()
        print()
        print(f"ERROR: {e}")
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_interactions()