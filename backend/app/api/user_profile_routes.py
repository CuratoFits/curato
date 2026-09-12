from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)

from app.api.dependencies import (
    get_user_profile_service,
)

from app.schemas.user import (
    UserProfileCreate,
    UserProfileResponse,
    UserProfileUpdate,
)

from app.service.user_profile_service import (
    UserProfileService,
)


router = APIRouter(
    prefix="/user-profiles",
    tags=["User Profiles"],
)


@router.get(
    "",
    response_model=list[UserProfileResponse],
)
def get_profiles(
    skip: int = Query(
        default=0,
        ge=0,
    ),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    service: UserProfileService = Depends(
        get_user_profile_service
    ),
):

    return service.get_profiles(
        skip=skip,
        limit=limit,
    )


@router.get(
    "/user/{user_id}",
    response_model=UserProfileResponse,
)
def get_profile_by_user_id(
    user_id: int,
    service: UserProfileService = Depends(
        get_user_profile_service
    ),
):

    profile = service.get_profile_by_user_id(
        user_id
    )

    if profile is None:

        raise HTTPException(
            status_code=404,
            detail="User profile not found",
        )

    return profile


@router.get(
    "/{profile_id}",
    response_model=UserProfileResponse,
)
def get_profile(
    profile_id: int,
    service: UserProfileService = Depends(
        get_user_profile_service
    ),
):

    profile = service.get_profile(
        profile_id
    )

    if profile is None:

        raise HTTPException(
            status_code=404,
            detail="User profile not found",
        )

    return profile


@router.post(
    "",
    response_model=UserProfileResponse,
    status_code=201,
)
def create_profile(
    profile: UserProfileCreate,
    service: UserProfileService = Depends(
        get_user_profile_service
    ),
):

    try:

        return service.create_profile(
            profile
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )


@router.patch(
    "/{profile_id}",
    response_model=UserProfileResponse,
)
def update_profile(
    profile_id: int,
    profile: UserProfileUpdate,
    service: UserProfileService = Depends(
        get_user_profile_service
    ),
):

    try:

        updated = service.update_profile(
            profile_id,
            profile,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    if updated is None:

        raise HTTPException(
            status_code=404,
            detail="User profile not found",
        )

    return updated


@router.delete(
    "/{profile_id}",
)
def delete_profile(
    profile_id: int,
    service: UserProfileService = Depends(
        get_user_profile_service
    ),
):

    deleted = service.delete_profile(
        profile_id
    )

    if not deleted:

        raise HTTPException(
            status_code=404,
            detail="User profile not found",
        )

    return {
        "message": "User profile deleted successfully"
    }