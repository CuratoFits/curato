from fastapi import HTTPException

from ..repository.repository import item_repository
from ..schemas.schema import CartItemRequest


class CartService:
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


cart_service = CartService()
