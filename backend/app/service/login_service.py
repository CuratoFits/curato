from fastapi import HTTPException

from ..repository.repository import item_repository
from ..schemas.schema import LoginRequest


class LoginService:
    def login(self, payload: LoginRequest, role: str):
        user = item_repository.authenticate_user(payload.username, payload.password, role)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        return {
            "message": "Login successful",
            "role": role,
            "user_id": user["id"],
        }


login_service = LoginService()
