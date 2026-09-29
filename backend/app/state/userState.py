from __future__ import annotations

from typing import Any, List, TypedDict
from app.agents.userBehaviorAgent import UserBehaviorAgent
from app.postgres.postgres import PostgresHandler
from app.agents.vectorDB_search_agent import VectorDBSearchAgent
class UserState():
    def __init__(self):
        self.user_id: str | None = None
        self.events: list[dict[str, Any]]= []
        self.user_preferences: list[dict[str, Any]] = []
        self.top_products: list[dict[str, Any]] = []

    def updateUserState(self,user_id: str) -> None:
        events = PostgresHandler.get_events_from_postgres(user_id)
        self.user_id = user_id
        self.events.extend(events)
        print(f"User state updated for user_id: {user_id} with events: {events}")
        
    def get_current_state(self, user_id: str) -> dict[str, Any]:
        if self.user_id == user_id:
            return {
                "events": self.events,
                "user_preferences": self.user_preferences,
                "top_products": self.top_products
            }
        else:
            print(f"User ID mismatch: expected {self.user_id}, got {user_id}")
            return {
                "events": [],
                "user_preferences": [],
                "top_products": []
            }
    
    def userPreferences(self, user_id: str) -> dict[str, Any]:
        insights = UserBehaviorAgent().user_behavior(user_id)
        self.user_preferences.extend(insights)
        print(f"User preferences updated for user_id: {user_id} with insights: {insights}")
            
    def get_user_id(self) -> str | None:
        return self.user_id        
    
    def add_top_products_to_userState(self, top_products: list[dict[str, Any]]) -> None:
        if self.user_id is None:
            print("User ID is not set. Cannot add top products to user state.")
        else:
            self.top_products.extend(top_products)
            print(f"Top products added to user state for user_id: {self.user_id} with products: {top_products}")
            
    def update_user_preferences(self, user_id: str, preferences: dict[str, Any]) -> None:
        if self.user_id == user_id:
            self.user_preferences.extend(preferences)
            print(f"User preferences updated for user_id: {user_id} with preferences: {preferences}")
        else:
            print(f"User ID mismatch: expected {self.user_id}, got {user_id}. Preferences not updated.")        
            
    def vectorDB_search(self) -> list[dict[str, Any]]:
        text=self.get_current_state(self.user_id)
        candidate_products= VectorDBSearchAgent().searchVectorDB(text)
        UserState.add_top_products_to_userState(self, candidate_products)
        print(f"VectorDB search completed for user_id: {self.user_id} with candidate products: {candidate_products}")    