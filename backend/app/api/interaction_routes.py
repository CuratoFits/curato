from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import get_interaction_service
from app.schemas.interaction import (
    InteractionEventCreate,
    InteractionEventResponse,
    InteractionEventUpdate,
)
from app.service.interaction_service import InteractionService


router = APIRouter(
    prefix="/interactions",
    tags=["Interactions"],
)


@router.get(
    "",
    response_model=List[InteractionEventResponse],
)
def get_interactions(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    service: InteractionService = Depends(
        get_interaction_service
    ),
):
    return service.get_interactions(
        skip=skip,
        limit=limit,
    )


@router.get(
    "/user/{user_id}",
    response_model=List[InteractionEventResponse],
)
def get_user_interactions(
    user_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    service: InteractionService = Depends(
        get_interaction_service
    ),
):
    return service.get_user_interactions(
        user_id=user_id,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/product/{product_id}",
    response_model=List[InteractionEventResponse],
)
def get_product_interactions(
    product_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    service: InteractionService = Depends(
        get_interaction_service
    ),
):
    return service.get_product_interactions(
        product_id=product_id,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{event_id}",
    response_model=InteractionEventResponse,
)
def get_interaction(
    event_id: int,
    service: InteractionService = Depends(
        get_interaction_service
    ),
):
    interaction = service.get_interaction(event_id)

    if interaction is None:
        raise HTTPException(
            status_code=404,
            detail="Interaction event not found",
        )

    return interaction


@router.post(
    "",
    response_model=InteractionEventResponse,
    status_code=201,
)
def create_interaction(
    interaction: InteractionEventCreate,
    service: InteractionService = Depends(
        get_interaction_service
    ),
):
    return service.create_interaction(
        interaction
    )


@router.patch(
    "/{event_id}",
    response_model=InteractionEventResponse,
)
def update_interaction(
    event_id: int,
    interaction: InteractionEventUpdate,
    service: InteractionService = Depends(
        get_interaction_service
    ),
):
    updated = service.update_interaction(
        event_id,
        interaction,
    )

    if updated is None:
        raise HTTPException(
            status_code=404,
            detail="Interaction event not found",
        )

    return updated


@router.delete(
    "/{event_id}",
)
def delete_interaction(
    event_id: int,
    service: InteractionService = Depends(
        get_interaction_service
    ),
):
    deleted = service.delete_interaction(event_id)

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Interaction event not found",
        )

    return {
        "message": "Interaction event deleted successfully"
    }