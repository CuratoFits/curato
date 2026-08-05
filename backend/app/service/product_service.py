from fastapi import HTTPException

from ..repository.repository import item_repository
from ..schemas.schema import ItemCreateRequest, ItemUpdateRequest


class ProductService:
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


product_service = ProductService()
