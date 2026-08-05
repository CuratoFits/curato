from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)

from app.api.dependencies import get_product_service
from app.schemas.product import (
    ProductCreate,
    ProductResponse,
    ProductUpdate,
)
from app.service.product_service import ProductService


router = APIRouter(
    prefix="/products",
    tags=["Products"],
)


@router.get(
    "",
    response_model=list[ProductResponse],
)
def get_products(
    skip: int = Query(default=0, ge=0),
    limit: int = Query(
        default=20,
        ge=1,
        le=100,
    ),
    service: ProductService = Depends(
        get_product_service
    ),
):
    return service.get_products(
        skip=skip,
        limit=limit,
    )


@router.get(
    "/category/{category}",
    response_model=list[ProductResponse],
)
def get_products_by_category(
    category: str,
    skip: int = 0,
    limit: int = 20,
    service: ProductService = Depends(
        get_product_service
    ),
):
    return service.get_products_by_category(
        category=category,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/{product_id}",
    response_model=ProductResponse,
)
def get_product(
    product_id: int,
    service: ProductService = Depends(
        get_product_service
    ),
):
    product = service.get_product(
        product_id
    )

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    return product


@router.post(
    "",
    response_model=ProductResponse,
    status_code=201,
)
def create_product(
    product: ProductCreate,
    service: ProductService = Depends(
        get_product_service
    ),
):
    return service.create_product(
        product
    )


@router.patch(
    "/{product_id}",
    response_model=ProductResponse,
)
def update_product(
    product_id: int,
    product: ProductUpdate,
    service: ProductService = Depends(
        get_product_service
    ),
):
    updated_product = service.update_product(
        product_id,
        product,
    )

    if updated_product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    return updated_product


@router.delete(
    "/{product_id}",
)
def delete_product(
    product_id: int,
    service: ProductService = Depends(
        get_product_service
    ),
):
    deleted = service.delete_product(
        product_id
    )

    if not deleted:
        raise HTTPException(
            status_code=404,
            detail="Product not found",
        )

    return {
        "message": "Product deleted successfully"
    }