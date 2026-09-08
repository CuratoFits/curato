from pathlib import Path

import pandas as pd
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert

from app.connections.connection import SessionLocal
from app.models.product import Product


# ---------------------------------------------------------
# Paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

CSV_PATH = BASE_DIR / "data" / "raw" / "products.csv"


# ---------------------------------------------------------
# Configuration
# ---------------------------------------------------------

BATCH_SIZE = 500


# ---------------------------------------------------------
# Seed products
# ---------------------------------------------------------

def seed_products() -> None:
    print(f"Reading products from: {CSV_PATH}")

    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"Products CSV not found: {CSV_PATH}"
        )

    df = pd.read_csv(CSV_PATH)

    print(f"Products found in CSV: {len(df)}")

    required_columns = [
        "product_id",
        "product_name",
        "category",
        "price",
        "description",
        "image_url",
        "product_url",
        "gender",
        "rating",
    ]

    missing_columns = [
        column for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Missing columns in products.csv: {missing_columns}"
        )

    # Replace pandas NaN values with Python None
    df = df.where(pd.notna(df), None)

    # Convert dataframe rows to dictionaries
    records = []

    for _, row in df.iterrows():
        record = {
            "id": int(row["product_id"]),
            "product_name": row["product_name"],
            "category": row["category"],
            "price": row["price"],
            "description": row["description"],
            "image_url": row["image_url"],
            "product_url": row["product_url"],
            "gender": row["gender"],
            "rating": row["rating"],
        }

        records.append(record)

    print(f"Prepared {len(records)} products for insertion.")

    db = SessionLocal()

    try:
        total = len(records)

        for start in range(0, total, BATCH_SIZE):
            batch = records[start:start + BATCH_SIZE]

            stmt = insert(Product).values(batch)

            # If product_url already exists, skip that product.
            stmt = stmt.on_conflict_do_nothing(
                index_elements=["product_url"]
            )

            db.execute(stmt)
            db.commit()

            end = min(start + BATCH_SIZE, total)

            print(
                f"Inserted batch: {end}/{total} products"
            )

        # -------------------------------------------------
        # Synchronize PostgreSQL ID sequence
        # -------------------------------------------------

        db.execute(
            text(
                """
                SELECT setval(
                    pg_get_serial_sequence('products', 'id'),
                    COALESCE(
                        (SELECT MAX(id) FROM products),
                        1
                    ),
                    true
                )
                """
            )
        )

        db.commit()

        # -------------------------------------------------
        # Verify
        # -------------------------------------------------

        count = db.execute(
            text("SELECT COUNT(*) FROM products")
        ).scalar_one()

        print()
        print("=" * 50)
        print("PRODUCT SEEDING COMPLETE")
        print("=" * 50)
        print(f"Products currently in database: {count}")
        print("=" * 50)

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


# ---------------------------------------------------------
# Entry point
# ---------------------------------------------------------

if __name__ == "__main__":
    seed_products()