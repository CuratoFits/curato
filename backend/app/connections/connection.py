import os
from contextlib import contextmanager

try:
    import pymysql
except Exception:  # pragma: no cover - optional during local backend-only setup
    pymysql = None


DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "curato")


def _ensure_mysql_available():
    if pymysql is None:
        raise RuntimeError("PyMySQL is not installed. Install it before attaching MySQL/XAMPP.")


@contextmanager
def get_root_connection():
    _ensure_mysql_available()
    connection = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )
    try:
        yield connection
    finally:
        connection.close()


@contextmanager
def get_db_connection():
    _ensure_mysql_available()
    connection = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )
    try:
        yield connection
    finally:
        connection.close()


def initialize_database():
    try:
        with get_root_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute("CREATE DATABASE IF NOT EXISTS curato;")
                cursor.execute("USE curato;")
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        username VARCHAR(100) NOT NULL UNIQUE,
                        password VARCHAR(255) NOT NULL,
                        role ENUM('admin','user') NOT NULL DEFAULT 'user'
                    );
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS items (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        name VARCHAR(200) NOT NULL,
                        category ENUM('clothes','shoes','heels','accessories') NOT NULL,
                        price DECIMAL(10,2) NOT NULL,
                        stock INT NOT NULL DEFAULT 0,
                        description TEXT,
                        image_url VARCHAR(500),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                    );
                    """
                )
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS carts (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        user_id INT NOT NULL,
                        item_id INT NOT NULL,
                        quantity INT NOT NULL DEFAULT 1,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users(id),
                        FOREIGN KEY (item_id) REFERENCES items(id)
                    );
                    """
                )
                cursor.execute(
                    """
                    INSERT INTO users (username, password, role)
                    VALUES ('admin', 'admin123', 'admin')
                    ON DUPLICATE KEY UPDATE password = VALUES(password), role = VALUES(role)
                    """
                )
                cursor.execute(
                    """
                    INSERT INTO users (username, password, role)
                    VALUES ('user', 'user123', 'user')
                    ON DUPLICATE KEY UPDATE password = VALUES(password), role = VALUES(role)
                    """
                )
    except Exception as exc:
        print(f"Database not attached yet. Backend will continue without DB startup seeding: {exc}")


def fetch_all(query: str, params: tuple | list | None = None):
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchall()


def fetch_one(query: str, params: tuple | list | None = None):
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchone()


def execute_query(query: str, params: tuple | list | None = None):
    with get_db_connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.lastrowid
