from abc import ABC, abstractmethod

from app.models.user import UserProfile
from app.schemas.user import (
    UserProfileCreate,
    UserProfileUpdate,
)


class UserProfileRepository(ABC):

    @abstractmethod
    def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
    ) -> list[UserProfile]:
        pass

    @abstractmethod
    def get_by_id(
        self,
        profile_id: int,
    ) -> UserProfile | None:
        pass

    @abstractmethod
    def get_by_user_id(
        self,
        user_id: int,
    ) -> UserProfile | None:
        pass

    @abstractmethod
    def create(
        self,
        profile: UserProfileCreate,
    ) -> UserProfile:
        pass

    @abstractmethod
    def update(
        self,
        profile_id: int,
        profile: UserProfileUpdate,
    ) -> UserProfile | None:
        pass

    @abstractmethod
    def delete(
        self,
        profile_id: int,
    ) -> bool:
        pass