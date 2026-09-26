import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Set root dir and backend dir in sys.path
BACKEND_DIR = Path(__file__).resolve().parents[1]
ROOT_DIR = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(BACKEND_DIR))
load_dotenv(ROOT_DIR / ".env")


SUPABASE_URL = os.getenv("SUPABASE_DATABASE_URL", os.getenv("DATABASE_URL"))
LOCAL_URL = os.getenv("LOCAL_DATABASE_URL")

def ensure_database_exists(url):
    from sqlalchemy.engine.url import make_url
    parsed = make_url(url)
    db_name = parsed.database
    if not db_name or db_name == "postgres":
        return

    root_url = parsed._replace(database="postgres").render_as_string(hide_password=False)
    root_engine = create_engine(root_url, isolation_level="AUTOCOMMIT")
    with root_engine.connect() as conn:
        res = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname='{db_name}'"))
        if not res.scalar():
            print(f"Database '{db_name}' does not exist locally. Creating database '{db_name}'...", flush=True)
            conn.execute(text(f"CREATE DATABASE {db_name}"))
            print(f"Database '{db_name}' created successfully.", flush=True)

def sync():
    if not SUPABASE_URL:
        print("Error: SUPABASE_DATABASE_URL is not set in .env", flush=True)
        return
    if not LOCAL_URL:
        print("Error: LOCAL_DATABASE_URL is not set in .env", flush=True)
        return

    try:
        ensure_database_exists(LOCAL_URL)
    except Exception as e:
        print(f"Warning during database creation check: {e}", flush=True)

    print("Connecting to Supabase and Local PostgreSQL...", flush=True)
    engine_supabase = create_engine(SUPABASE_URL, pool_pre_ping=True)
    engine_local = create_engine(LOCAL_URL, pool_pre_ping=True)

    from app.db.base import Base
    from app.models.product import Product
    from app.models.user import UserProfile
    from app.models.interaction import InteractionEvent

    # Create tables on local database if they don't exist
    print("Ensuring tables exist on local database...", flush=True)
    Base.metadata.create_all(bind=engine_local)

    SessionSupabase = sessionmaker(bind=engine_supabase)
    SessionLocal = sessionmaker(bind=engine_local)

    db_supa = SessionSupabase()
    db_loc = SessionLocal()

    try:
        # Sync Products
        print("Syncing Products...", flush=True)
        products = db_supa.query(Product).all()
        for p in products:
            db_loc.merge(Product(
                id=p.id,
                product_name=p.product_name,
                category=p.category,
                price=p.price,
                description=p.description,
                image_url=p.image_url,
                product_url=p.product_url,
                gender=p.gender,
                rating=p.rating,
                created_at=p.created_at,
                updated_at=p.updated_at
            ))
        db_loc.commit()
        print(f"Synced {len(products)} products.", flush=True)

        # Sync User Profiles
        print("Syncing User Profiles...", flush=True)
        users = db_supa.query(UserProfile).all()
        for u in users:
            db_loc.merge(UserProfile(
                id=u.id,
                user_id=u.user_id,
                age=u.age,
                preferred_min_price=u.preferred_min_price,
                preferred_max_price=u.preferred_max_price,
                preferred_categories=u.preferred_categories,
                preferred_rating=u.preferred_rating
            ))
        db_loc.commit()
        print(f"Synced {len(users)} user profiles.", flush=True)

        # Sync Interaction Events
        print("Syncing Interaction Events...", flush=True)
        events = db_supa.query(InteractionEvent).all()
        for e in events:
            db_loc.merge(InteractionEvent(
                event_id=e.event_id,
                user_id=e.user_id,
                product_id=e.product_id,
                event_type=e.event_type,
                session_id=e.session_id,
                time_spent_seconds=e.time_spent_seconds,
                scroll_depth=e.scroll_depth,
                source=e.source,
                quantity=e.quantity,
                timestamp=e.timestamp
            ))
        db_loc.commit()
        print(f"Synced {len(events)} interaction events.", flush=True)

        print("SUCCESS! All data synchronized from Supabase to Local PostgreSQL.", flush=True)

    except Exception as err:
        db_loc.rollback()
        print(f"Error during database sync: {err}", flush=True)
    finally:
        db_supa.close()
        db_loc.close()

if __name__ == "__main__":
    sync()
