from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from ..schemas.schema import (
    CartItemRequest,
    ItemCreateRequest,
    ItemUpdateRequest,
    LoginRequest,
    LoginResponse,
    MessageResponse,
)
from ..service.cart_service import cart_service
from ..service.login_service import login_service
from ..service.product_service import product_service

router = APIRouter()
security = HTTPBasic()


def verify_simple_auth(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username == "admin" and credentials.password == "admin123":
        return {"role": "admin"}
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")


@router.post("/admin/login", response_model=LoginResponse)
def admin_login(payload: LoginRequest):
    return login_service.login(payload, role="admin")


@router.post("/user/login", response_model=LoginResponse)
def user_login(payload: LoginRequest):
    return login_service.login(payload, role="user")


@router.get("/items")
def list_items():
    return product_service.get_all_items()


@router.post("/admin/items", response_model=MessageResponse)
def create_item(payload: ItemCreateRequest, auth=Depends(verify_simple_auth)):
    if auth["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return product_service.create_item(payload)


@router.put("/admin/items/{item_id}", response_model=MessageResponse)
def update_item(item_id: int, payload: ItemUpdateRequest, auth=Depends(verify_simple_auth)):
    if auth["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return product_service.update_item(item_id, payload)


@router.delete("/admin/items/{item_id}", response_model=MessageResponse)
def delete_item(item_id: int, auth=Depends(verify_simple_auth)):
    if auth["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return product_service.delete_item(item_id)


@router.get("/user/cart/{user_id}")
def get_cart(user_id: int):
    return cart_service.get_cart(user_id)


@router.post("/user/cart/{user_id}", response_model=MessageResponse)
def add_to_cart(user_id: int, payload: CartItemRequest):
    return cart_service.add_to_cart(user_id, payload)


@router.delete("/user/cart/{user_id}/{item_id}", response_model=MessageResponse)
def remove_from_cart(user_id: int, item_id: int):
    return cart_service.remove_from_cart(user_id, item_id)


@router.delete("/user/cart/{user_id}/clear", response_model=MessageResponse)
def clear_cart(user_id: int):
    return cart_service.clear_cart(user_id)
