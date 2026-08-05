from __future__ import annotations

from typing import Any, TypedDict


class UserState(TypedDict, total=False):
    """Per-user LangGraph state for event ingestion.

    - user_id: the owning user identifier
    - events: a list of event payloads collected for the user
    - preferences: a dictionary for user preference settings
    - updated_at: optional timestamp marker for the latest state change
    """

    user_id: int
    events: list[dict[str, Any]]
    preferences: dict[str, Any]
    updated_at: str | None


DEFAULT_USER_PREFERENCES: dict[str, Any] = {}
