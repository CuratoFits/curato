"""add enriched columns to products and user_profiles

Revision ID: a1b2c3d4e5f6
Revises: f6e4cdd8a06c
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "f6e4cdd8a06c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

PRODUCT_COLS = [
    ("subcategory", sa.String(150)), ("brand", sa.String(150)),
    ("original_price", sa.Float()), ("discount", sa.Float()),
    ("color", sa.String(100)), ("material", sa.String(150)),
    ("style", sa.String(150)), ("occasion", sa.String(150)),
    ("fit", sa.String(100)), ("season", sa.String(100)),
    ("availability", sa.String(50)),
]
USER_COLS = [
    ("gender", sa.String(50)), ("city", sa.String(100)),
    ("state", sa.String(100)), ("country", sa.String(100)),
    ("preferred_brands", sa.String(500)), ("preferred_colors", sa.String(500)),
    ("preferred_sizes", sa.String(500)), ("preferred_materials", sa.String(500)),
    ("preferred_styles", sa.String(500)), ("preferred_occasions", sa.String(500)),
]


def upgrade() -> None:
    for name, typ in PRODUCT_COLS:
        op.add_column("products", sa.Column(name, typ, nullable=True))
    op.create_index(op.f("ix_products_brand"), "products", ["brand"], unique=False)
    for name, typ in USER_COLS:
        op.add_column("user_profiles", sa.Column(name, typ, nullable=True))


def downgrade() -> None:
    for name, _ in reversed(USER_COLS):
        op.drop_column("user_profiles", name)
    op.drop_index(op.f("ix_products_brand"), table_name="products")
    for name, _ in reversed(PRODUCT_COLS):
        op.drop_column("products", name)