from app.repository.interfaces.user_profile_repository import (
    UserProfileRepository,
)
from app.schemas.user import (
    UserProfileCreate,
    UserProfileUpdate,
)


class UserProfileService:

    def __init__(
        self,
        repository: UserProfileRepository,
    ):
        self.repository = repository

    def get_profiles(
        self,
        skip: int = 0,
        limit: int = 20,
    ):

        return self.repository.get_all(
            skip=skip,
            limit=limit,
        )

    def get_profile(
        self,
        profile_id: int,
    ):

        return self.repository.get_by_id(
            profile_id
        )

    def get_profile_by_user_id(
        self,
        user_id: int,
    ):

        return self.repository.get_by_user_id(
            user_id
        )

    def create_profile(
        self,
        profile: UserProfileCreate,
    ):

        if (
            profile.preferred_min_price
            > profile.preferred_max_price
        ):
            raise ValueError(
                "Minimum price cannot be greater "
                "than maximum price"
            )

        return self.repository.create(
            profile
        )

    def update_profile(
        self,
        profile_id: int,
        profile: UserProfileUpdate,
    ):

        if (
            profile.preferred_min_price is not None
            and profile.preferred_max_price is not None
            and profile.preferred_min_price
            > profile.preferred_max_price
        ):
            raise ValueError(
                "Minimum price cannot be greater "
                "than maximum price"
            )

        return self.repository.update(
            profile_id,
            profile,
        )

    def delete_profile(
        self,
        profile_id: int,
    ):

        return self.repository.delete(
            profile_id
        )