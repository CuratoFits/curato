from sqlalchemy import Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)

    user_id: Mapped[int] = mapped_column(Integer, nullable=False, unique=True, index=True)

    age: Mapped[int] = mapped_column(Integer, nullable=False)
    gender: Mapped[str] = mapped_column(String(50), nullable=True)

    city: Mapped[str] = mapped_column(String(100), nullable=True)
    state: Mapped[str] = mapped_column(String(100), nullable=True)
    country: Mapped[str] = mapped_column(String(100), nullable=True)

    preferred_min_price: Mapped[float] = mapped_column(Float, nullable=False)
    preferred_max_price: Mapped[float] = mapped_column(Float, nullable=False)
    preferred_rating: Mapped[float] = mapped_column(Float, nullable=False)

    preferred_categories: Mapped[str] = mapped_column(String(500), nullable=False)
    preferred_brands: Mapped[str] = mapped_column(String(500), nullable=True)
    preferred_colors: Mapped[str] = mapped_column(String(500), nullable=True)
    preferred_sizes: Mapped[str] = mapped_column(String(500), nullable=True)
    preferred_materials: Mapped[str] = mapped_column(String(500), nullable=True)
    preferred_styles: Mapped[str] = mapped_column(String(500), nullable=True)
    preferred_occasions: Mapped[str] = mapped_column(String(500), nullable=True)