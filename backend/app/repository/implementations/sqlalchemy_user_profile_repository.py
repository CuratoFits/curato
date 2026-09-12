from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import UserProfile
from app.repository.interfaces.user_profile_repository import (
    UserProfileRepository,
)
from app.schemas.user import (
    UserProfileCreate,
    UserProfileUpdate,
)


class SQLAlchemyUserProfileRepository(
    UserProfileRepository
):

    def __init__(self, db: Session):
        self.db = db

    def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
    ) -> list[UserProfile]:

        statement = (
            select(UserProfile)
            .offset(skip)
            .limit(limit)
        )

        return list(
            self.db.scalars(statement).all()
        )

    def get_by_id(
        self,
        profile_id: int,
    ) -> UserProfile | None:

        return self.db.get(
            UserProfile,
            profile_id,
        )

    def get_by_user_id(
        self,
        user_id: int,
    ) -> UserProfile | None:

        statement = (
            select(UserProfile)
            .where(
                UserProfile.user_id == user_id
            )
        )

        return self.db.scalars(
            statement
        ).first()

    def create(
        self,
        profile: UserProfileCreate,
    ) -> UserProfile:

        db_profile = UserProfile(
            **profile.model_dump()
        )

        self.db.add(db_profile)

        self.db.commit()

        self.db.refresh(db_profile)

        return db_profile

    def update(
        self,
        profile_id: int,
        profile: UserProfileUpdate,
    ) -> UserProfile | None:

        db_profile = self.get_by_id(
            profile_id
        )

        if db_profile is None:
            return None

        update_data = profile.model_dump(
            exclude_unset=True
        )

        for field, value in update_data.items():

            setattr(
                db_profile,
                field,
                value
            )

        self.db.commit()

        self.db.refresh(db_profile)

        return db_profile

    def delete(
        self,
        profile_id: int,
    ) -> bool:

        db_profile = self.get_by_id(
            profile_id
        )

        if db_profile is None:
            return False

        self.db.delete(db_profile)

        self.db.commit()

        return True