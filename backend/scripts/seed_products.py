from pathlib import Path

import pandas as pd
from sqlalchemy import select, text

from app.connections.connection import SessionLocal
from app.models.product import Product


# ---------------------------------------------------------
# File paths
# ---------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]

CSV_PATH = BASE_DIR / "data" / "products.csv"


# ---------------------------------------------------------
# Utility functions
# ---------------------------------------------------------

def clean_value(value):
    """
    Convert pandas NaN values to None.

    This ensures missing CSV values are stored as
    PostgreSQL NULL instead of pandas NaN.
    """

    if pd.isna(value):
        return None

    return value


# ---------------------------------------------------------
# Product seeding
# ---------------------------------------------------------

def seed_products():

    print(f"Reading products from: {CSV_PATH}")

    # Make sure CSV exists
    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"Products CSV not found: {CSV_PATH}"
        )

    # Read CSV
    df = pd.read_csv(CSV_PATH)

    print(f"Products found in CSV: {len(df)}")

    db = SessionLocal()

    inserted = 0
    skipped = 0

    try:

        # -------------------------------------------------
        # Get product URLs already stored in PostgreSQL
        # -------------------------------------------------

        existing_urls = set(
            db.scalars(
                select(Product.product_url)
            ).all()
        )

        products = []

        # -------------------------------------------------
        # Convert CSV rows into Product objects
        # -------------------------------------------------

        for _, row in df.iterrows():

            product_url = clean_value(
                row["product_url"]
            )

            # ---------------------------------------------
            # Skip products already in database
            # ---------------------------------------------

            if product_url in existing_urls:
                skipped += 1
                continue

            # ---------------------------------------------
            # Create SQLAlchemy Product object
            # ---------------------------------------------

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

            products.append(product)

            # Prevent duplicates inside the same CSV
            if product_url:
                existing_urls.add(product_url)

        # -------------------------------------------------
        # Insert products
        # -------------------------------------------------

        if products:

            db.add_all(products)

            db.commit()

            inserted = len(products)

        # -------------------------------------------------
        # Synchronize PostgreSQL ID sequence
        # -------------------------------------------------
        #
        # We manually imported IDs from the CSV:
        #
        # 1 ... 2321
        #
        # PostgreSQL's automatic ID sequence therefore needs
        # to be synchronized with the highest existing ID.
        #
        # After this, a newly created product will receive:
        #
        # 2322
        # -------------------------------------------------

        db.execute(
            text(
                """
                SELECT setval(
                    pg_get_serial_sequence('products', 'id'),
                    COALESCE(
                        (SELECT MAX(id) FROM products),
                        1
                    )
                )
                """
            )
        )

        db.commit()

        # -------------------------------------------------
        # Results
        # -------------------------------------------------

        print("\nCatalog seeding completed.")
        print(f"Inserted: {inserted}")
        print(f"Skipped: {skipped}")
        print(f"CSV total: {len(df)}")

    except Exception as exc:

        # Undo uncommitted database operations
        db.rollback()

        print("\nCatalog seeding failed.")
        print(f"Error: {exc}")

        raise

    finally:

        db.close()


# ---------------------------------------------------------
# Script entry point
# ---------------------------------------------------------

if __name__ == "__main__":
    seed_products()