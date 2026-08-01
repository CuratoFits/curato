from dataclasses import dataclass
from enum import Enum


class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"


class ItemCategory(str, Enum):
    CLOTHES = "clothes"
    SHOES = "shoes"
    HEELS = "heels"
    ACCESSORIES = "accessories"


@dataclass
class UserModel:
    username: str
    password: str
    role: UserRole


@dataclass
class ItemModel:
    name: str
    category: ItemCategory
    price: float
    stock: int
    description: str | None = None
    image_url: str | None = None


@dataclass
class CartItemModel:
    user_id: int
    item_id: int
    quantity: int = 1


CREATE_TABLE_SQL = """
CREATE DATABASE IF NOT EXISTS curato;
USE curato;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role ENUM('admin','user') NOT NULL DEFAULT 'user'
);

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
