from app.repository.interfaces.interaction_repository import (
    InteractionRepository,
)
from app.schemas.interaction import (
    InteractionEventCreate,
    InteractionEventUpdate,
)


class InteractionService:

    def __init__(
        self,
        repository: InteractionRepository,
    ):
        self.repository = repository

    def get_interactions(
        self,
        skip: int = 0,
        limit: int = 20,
    ):
        return self.repository.get_all(
            skip=skip,
            limit=limit,
        )

    def get_interaction(
        self,
        event_id: int,
    ):
        return self.repository.get_by_id(
            event_id
        )

    def get_user_interactions(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
    ):
        return self.repository.get_by_user_id(
            user_id=user_id,
            skip=skip,
            limit=limit,
        )

    def get_product_interactions(
        self,
        product_id: int,
        skip: int = 0,
        limit: int = 20,
    ):
        return self.repository.get_by_product_id(
            product_id=product_id,
            skip=skip,
            limit=limit,
        )

    def create_interaction(
        self,
        interaction: InteractionEventCreate,
    ):
        return self.repository.create(
            interaction
        )

    def update_interaction(
        self,
        event_id: int,
        interaction: InteractionEventUpdate,
    ):
        return self.repository.update(
            event_id,
            interaction,
        )

    def delete_interaction(
        self,
        event_id: int,
    ):
        return self.repository.delete(
            event_id
        )