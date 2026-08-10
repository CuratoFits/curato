from __future__ import annotations

from typing import Any, TypedDict


class UserState(TypedDict, total=False):
    user_id: int
    events: list[dict[str, Any]]
    preferences: dict[str, Any]
    updated_at: str | None


DEFAULT_USER_PREFERENCES: dict[str, Any] = {}
