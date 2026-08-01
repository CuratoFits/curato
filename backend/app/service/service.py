from fastapi import HTTPException

from repository.repository import item_repository
from schemas.schema import (
    CartItemRequest,
    ItemCreateRequest,
    ItemUpdateRequest,
    LoginRequest,
)


class ItemService:
    def login(self, payload: LoginRequest, role: str):
        user = item_repository.authenticate_user(payload.username, payload.password, role)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        return {
            "message": "Login successful",
            "role": role,
            "user_id": user["id"],
        }

    def get_all_items(self):
        return item_repository.get_all_items()

    def create_item(self, payload: ItemCreateRequest):
        item_id = item_repository.create_item(payload.model_dump())
        return {
            "message": "Item created successfully",
            "item_id": item_id,
        }

    def update_item(self, item_id: int, payload: ItemUpdateRequest):
        existing_item = item_repository.get_item_by_id(item_id)
        if not existing_item:
            raise HTTPException(status_code=404, detail="Item not found")

        item_repository.update_item(item_id, payload.model_dump(exclude_unset=True))
        return {
            "message": "Item updated successfully",
            "item_id": item_id,
        }

    def delete_item(self, item_id: int):
        existing_item = item_repository.get_item_by_id(item_id)
        if not existing_item:
            raise HTTPException(status_code=404, detail="Item not found")
        item_repository.delete_item(item_id)
        return {"message": "Item removed successfully"}

    def add_to_cart(self, user_id: int, payload: CartItemRequest):
        item = item_repository.get_item_by_id(payload.item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        if payload.quantity > item["stock"]:
            raise HTTPException(status_code=400, detail="Requested quantity exceeds stock")

        item_repository.upsert_cart_item(user_id, payload.item_id, payload.quantity)
        return {"message": "Item added to cart"}

    def get_cart(self, user_id: int):
        return item_repository.get_cart_items(user_id)

    def remove_from_cart(self, user_id: int, item_id: int):
        item_repository.remove_cart_item(user_id, item_id)
        return {"message": "Item removed from cart"}

    def clear_cart(self, user_id: int):
        item_repository.clear_cart(user_id)
        return {"message": "Cart cleared"}


item_service = ItemService()
