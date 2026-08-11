import pandas as pd

from app.models.product import Product
from scripts.seed_products import CSV_PATH, clean_value


EXPECTED_COLUMNS = {
    "product_id",
    "product_name",
    "category",
    "price",
    "description",
    "image_url",
    "product_url",
    "gender",
    "rating",
}


# ---------------------------------------------------------
# CSV EXISTENCE
# ---------------------------------------------------------

def test_products_csv_exists():

    assert CSV_PATH.exists()


# ---------------------------------------------------------
# CSV COLUMNS
# ---------------------------------------------------------

def test_products_csv_columns():

    df = pd.read_csv(CSV_PATH)

    assert EXPECTED_COLUMNS.issubset(
        set(df.columns)
    )


# ---------------------------------------------------------
# ROW COUNT
# ---------------------------------------------------------

def test_products_csv_row_count():

    df = pd.read_csv(CSV_PATH)

    assert len(df) == 2321


# ---------------------------------------------------------
# PRODUCT IDS
# ---------------------------------------------------------

def test_product_ids_are_unique():

    df = pd.read_csv(CSV_PATH)

    assert df["product_id"].is_unique


# ---------------------------------------------------------
# PRODUCT URLS
# ---------------------------------------------------------

def test_product_urls_are_unique():

    df = pd.read_csv(CSV_PATH)

    urls = df["product_url"].dropna()

    assert urls.is_unique


# ---------------------------------------------------------
# PRODUCT NAMES
# ---------------------------------------------------------

def test_required_product_names_exist():

    df = pd.read_csv(CSV_PATH)

    assert df["product_name"].notna().all()


# ---------------------------------------------------------
# RATINGS
# ---------------------------------------------------------

def test_rating_range():

    df = pd.read_csv(CSV_PATH)

    ratings = df["rating"].dropna()

    assert ratings.between(
        1.0,
        5.0
    ).all()


# ---------------------------------------------------------
# GENDER
# ---------------------------------------------------------

def test_gender_is_women():

    df = pd.read_csv(CSV_PATH)

    genders = set(
        df["gender"]
        .dropna()
        .unique()
    )

    assert genders == {"Women"}


# ---------------------------------------------------------
# CLEAN VALUE
# ---------------------------------------------------------

def test_clean_value_converts_nan_to_none():

    assert clean_value(
        float("nan")
    ) is None


def test_clean_value_keeps_normal_value():

    assert clean_value(
        "Shirt"
    ) == "Shirt"


# ---------------------------------------------------------
# PRODUCT CREATION
# ---------------------------------------------------------

def test_csv_row_can_create_product():

    df = pd.read_csv(CSV_PATH)

    row = df.iloc[0]

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
        product_url=clean_value(
            row["product_url"]
        ),
        gender=clean_value(
            row["gender"]
        ),
        rating=clean_value(
            row["rating"]
        ),
    )

    assert product.id == int(
        row["product_id"]
    )

    assert product.product_name == (
        row["product_name"]
    )

    assert product.rating == (
        row["rating"]
    )