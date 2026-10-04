from pathlib import Path

import pandas as pd
from sqlalchemy import text
from sqlalchemy.dialects.postgresql import insert

from app.connections.connection import SessionLocal
from app.models.product import Product

BASE_DIR = Path(__file__).resolve().parents[1]
CSV_PATH = BASE_DIR / "data" / "raw" / "products.csv"
BATCH_SIZE = 500

# CSV column "product_id" -> DB column "id"; all other columns share the model's names.
MODEL_COLUMNS = [
    "product_name", "category", "subcategory", "brand", "gender", "price",
    "original_price", "discount", "color", "material", "style", "occasion",
    "fit", "season", "description", "rating", "availability", "image_url",
    "product_url",
]


def seed_products() -> None:
    print(f"Reading products from: {CSV_PATH}")
    df = pd.read_csv(CSV_PATH)
    print(f"Products found in CSV: {len(df)}")

    missing = [c for c in ["product_id", *MODEL_COLUMNS] if c not in df.columns]
    if missing:
        raise ValueError(f"Missing columns in products.csv: {missing}")

    df = df.astype(object).where(pd.notna(df), None)

    records = []
    for row in df.to_dict(orient="records"):
        record = {"id": int(row["product_id"])}
        for col in MODEL_COLUMNS:
            record[col] = row[col]
        records.append(record)

    print(f"Prepared {len(records)} products for insertion.")

    db = SessionLocal()
    try:
        for start in range(0, len(records), BATCH_SIZE):
            batch = records[start:start + BATCH_SIZE]
            stmt = insert(Product).values(batch)
            stmt = stmt.on_conflict_do_nothing(index_elements=["product_url"])
            db.execute(stmt)
            db.commit()
            print(f"Inserted batch: {min(start + BATCH_SIZE, len(records))}/{len(records)} products")

        # keep the id sequence ahead of the imported ids
        db.execute(text(
            "SELECT setval(pg_get_serial_sequence('products','id'),"
            " COALESCE((SELECT MAX(id) FROM products),1), true)"
        ))
        db.commit()

        count = db.execute(text("SELECT COUNT(*) FROM products")).scalar_one()
        print("\n" + "=" * 50)
        print("PRODUCT SEEDING COMPLETE")
        print("=" * 50)
        print(f"Products currently in database: {count}")
        print("=" * 50)
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_products()