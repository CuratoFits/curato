from connections.connection import execute_query, fetch_all, fetch_one


class ItemRepository:
    def get_all_items(self):
        return fetch_all(
            """
            SELECT id, name, category, price, stock, description, image_url
            FROM items
            ORDER BY created_at DESC
            """
        )

    def get_item_by_id(self, item_id: int):
        return fetch_one(
            """
            SELECT id, name, category, price, stock, description, image_url
            FROM items
            WHERE id = %s
            """,
            (item_id,),
        )

    def create_item(self, payload: dict):
        query = """
            INSERT INTO items (name, category, price, stock, description, image_url)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        return execute_query(query, (
            payload["name"],
            payload["category"],
            payload["price"],
            payload["stock"],
            payload.get("description"),
            payload.get("image_url"),
        ))

    def update_item(self, item_id: int, payload: dict):
        allowed_fields = [
            "name",
            "category",
            "price",
            "stock",
            "description",
            "image_url",
        ]
        updates = []
        values = []
        for key in allowed_fields:
            if key in payload and payload[key] is not None:
                updates.append(f"{key} = %s")
                values.append(payload[key])

        if not updates:
            return None

        values.append(item_id)
        query = f"UPDATE items SET {', '.join(updates)} WHERE id = %s"
        return execute_query(query, tuple(values))

    def delete_item(self, item_id: int):
        return execute_query("DELETE FROM items WHERE id = %s", (item_id,))

    def authenticate_user(self, username: str, password: str, role: str):
        return fetch_one(
            """
            SELECT id, username, role
            FROM users
            WHERE username = %s AND password = %s AND role = %s
            """,
            (username, password, role),
        )

    def create_user(self, username: str, password: str, role: str):
        return execute_query(
            """
            INSERT INTO users (username, password, role)
            VALUES (%s, %s, %s)
            """,
            (username, password, role),
        )

    def get_cart_items(self, user_id: int):
        return fetch_all(
            """
            SELECT c.id, c.user_id, c.item_id, c.quantity, i.name, i.price
            FROM carts c
            JOIN items i ON c.item_id = i.id
            WHERE c.user_id = %s
            """,
            (user_id,),
        )

    def upsert_cart_item(self, user_id: int, item_id: int, quantity: int):
        existing = fetch_one(
            "SELECT id FROM carts WHERE user_id = %s AND item_id = %s",
            (user_id, item_id),
        )
        if existing:
            return execute_query(
                "UPDATE carts SET quantity = quantity + %s WHERE user_id = %s AND item_id = %s",
                (quantity, user_id, item_id),
            )
        return execute_query(
            "INSERT INTO carts (user_id, item_id, quantity) VALUES (%s, %s, %s)",
            (user_id, item_id, quantity),
        )

    def remove_cart_item(self, user_id: int, item_id: int):
        return execute_query(
            "DELETE FROM carts WHERE user_id = %s AND item_id = %s",
            (user_id, item_id),
        )

    def clear_cart(self, user_id: int):
        return execute_query("DELETE FROM carts WHERE user_id = %s", (user_id,))


item_repository = ItemRepository()
