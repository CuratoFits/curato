from __future__ import annotations

from typing import Any, List, TypedDict
from app.agents.userBehaviorAgent import UserBehaviorAgent

class UserState():
    def __init__(self):
        self.user_id: str | None = None
        self.events: list[dict[str, Any]]= []
        self.user_preferences: list[dict[str, Any]] = {}

    def updateUserState(self,user_id: str, events: list[dict[str, Any]]) -> None:
        self.user_id = user_id
        self.events.extend(events)
        print(f"User state updated for user_id: {user_id} with events: {events}")
        
    def get_current_state(self, user_id: str) -> dict[str, Any]:
        if self.user_id == user_id:
            return {
                "events": self.events
            }
        else:
            print(f"User ID mismatch: expected {self.user_id}, got {user_id}")
            return {
                "events": []
            }

    def userPreferences(self, user_id: str) -> dict[str, Any]:
        insights = UserBehaviorAgent().user_behavior(user_id)
        self.user_preferences.extend(insights)
        print(f"User preferences updated for user_id: {user_id} with insights: {insights}")
            