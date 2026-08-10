from __future__ import annotations

from typing import Any, List, TypedDict


class UserState():
    def __init__(self):
        self.user_id: str | None = None
        self.events: list[dict[str, Any]]= []

    def updateUserState(self,user_id: str, events: list[dict[str, Any]]) -> None:
        self.user_id = user_id
        self.events.extend(events)
