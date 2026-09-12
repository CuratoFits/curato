from sqlalchemy import text
from app.connections.connection import engine

def test_supabase_database_connection():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        assert result.scalar() == 1
