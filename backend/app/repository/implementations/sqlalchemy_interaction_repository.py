from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.interaction import InteractionEvent
from app.repository.interfaces.interaction_repository import (
    InteractionRepository,
)
from app.schemas.interaction import (
    InteractionEventCreate,
    InteractionEventUpdate,
)


class SQLAlchemyInteractionRepository(
    InteractionRepository
):

    def __init__(self, db: Session):

        self.db = db

    def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
    ):

        return self.db.scalars(
            select(InteractionEvent)
            .offset(skip)
            .limit(limit)
        ).all()

    def get_by_id(
        self,
        event_id: int,
    ):

        return self.db.get(
            InteractionEvent,
            event_id,
        )

    def get_by_user_id(
        self,
        user_id: int,
        skip: int = 0,
        limit: int = 20,
    ):

        return self.db.scalars(
            select(InteractionEvent)
            .where(
                InteractionEvent.user_id
                == user_id
            )
            .offset(skip)
            .limit(limit)
        ).all()

    def get_by_product_id(
        self,
        product_id: int,
        skip: int = 0,
        limit: int = 20,
    ):

        return self.db.scalars(
            select(InteractionEvent)
            .where(
                InteractionEvent.product_id
                == product_id
            )
            .offset(skip)
            .limit(limit)
        ).all()

    def create(
        self,
        interaction: InteractionEventCreate,
    ):

        event = InteractionEvent(
            **interaction.model_dump()
        )

        self.db.add(event)
        self.db.commit()
        self.db.refresh(event)

        return event

    def update(
        self,
        event_id: int,
        interaction: InteractionEventUpdate,
    ):

        event = self.get_by_id(event_id)

        if event is None:
            return None

        data = interaction.model_dump(
            exclude_unset=True
        )

        for key, value in data.items():

            setattr(
                event,
                key,
                value,
            )

        self.db.commit()
        self.db.refresh(event)

        return event

    def delete(
        self,
        event_id: int,
    ):

        event = self.get_by_id(event_id)

        if event is None:
            return False

        self.db.delete(event)
        self.db.commit()

        return True