from pathlib import Path

import math

import pandas as pd
from sqlalchemy import text

from app.connections.connection import SessionLocal
from app.models.product import Product


# ---------------------------------------------------------
# PATHS
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

CSV_PATH = BASE_DIR / "data" / "raw" / "products.csv"


# ---------------------------------------------------------
# HELPER
# ---------------------------------------------------------

def clean_value(value):
    """
    Convert pandas NaN values to None.

    Normal values are returned unchanged.
    """

    if value is None:
        return None

    if isinstance(value, float) and math.isnan(value):
        return None

    return value


# ---------------------------------------------------------
# SEED PRODUCTS
# ---------------------------------------------------------

def seed_products():

    print(f"Reading products from: {CSV_PATH}")

    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"Products CSV not found: {CSV_PATH}"
        )

    df = pd.read_csv(CSV_PATH)

    print(f"Products found in CSV: {len(df)}")

    db = SessionLocal()

    inserted = 0
    skipped = 0

    try:

        for _, row in df.iterrows():

            product_url = clean_value(
                row["product_url"]
            )

            # -------------------------------------------------
            # Skip product if it already exists
            # -------------------------------------------------

            if product_url is not None:

                existing = (
                    db.query(Product)
                    .filter(
                        Product.product_url
                        == product_url
                    )
                    .first()
                )

                if existing is not None:
                    skipped += 1
                    continue

            # -------------------------------------------------
            # Create product
            # -------------------------------------------------

            product = Product(
                id=int(row["product_id"]),
                product_name=clean_value(
                    row["product_name"]
                ),
                category=clean_value(
                    row["category"]
                ),
                price=clean_value(
                    row["price"]
                ),
                description=clean_value(
                    row["description"]
                ),
                image_url=clean_value(
                    row["image_url"]
                ),
                product_url=product_url,
                gender=clean_value(
                    row["gender"]
                ),
                rating=clean_value(
                    row["rating"]
                ),
            )

            db.add(product)

            inserted += 1

        # -----------------------------------------------------
        # Commit products
        # -----------------------------------------------------

        db.commit()

        # -----------------------------------------------------
        # Synchronize PostgreSQL ID sequence
        # -----------------------------------------------------

        db.execute(
            text(
                """
                SELECT setval(
                    pg_get_serial_sequence(
                        'products',
                        'id'
                    ),
                    COALESCE(
                        (SELECT MAX(id) FROM products),
                        1
                    )
                )
                """
            )
        )

        db.commit()

        print()
        print("Catalog seeding completed.")
        print(f"Inserted: {inserted}")
        print(f"Skipped: {skipped}")
        print(f"CSV total: {len(df)}")

    except Exception:

        db.rollback()

        raise

    finally:

        db.close()


# ---------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------

if __name__ == "__main__":
    seed_products()