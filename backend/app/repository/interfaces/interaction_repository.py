from abc import ABC, abstractmethod

from app.schemas.interaction import (
    InteractionEventCreate,
    InteractionEventUpdate,
)


class InteractionRepository(ABC):

    @abstractmethod
    def get_all(self,skip: int = 0,limit: int = 20)-> list[InteractionEvent]:
        pass

    @abstractmethod
    def get_by_id(self,event_id: int) -> InteractionEvent | None:
        pass

    @abstractmethod
    def get_by_user_id(self,user_id: int,skip: int = 0,limit: int = 20) -> list[InteractionEvent]:
        pass

    @abstractmethod
    def get_by_product_id(self,product_id: int,skip: int = 0,limit: int = 20) -> list[InteractionEvent]:
        pass

    @abstractmethod
    def create(self,interaction: InteractionEventCreate) -> InteractionEvent:
        pass

    @abstractmethod
    def update(self,event_id: int,interaction: InteractionEventUpdate) -> InteractionEvent:
        pass

    @abstractmethod
    def delete(self,event_id: int) -> None:
        pass