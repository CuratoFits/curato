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
        
    def get_current_state(self, user_id: str) -> dict[str, Any]:
        self.user_id= user_id
        events= PostgresHandler().get_current_interaction_events(user_id)
        recent_events=[]
        for event in events:
            prod_id= event.product_id
            event_type= event.event_type
            recent_events.append({"product_id": prod_id, "event_type": event_type})
        self.events= recent_events
        self.user_preferences= UserBehaviorAgent.user_behavior(user_id) 
        current_state={
            "user_id": self.user_id,
            "events": self.events,
            "user_preferences": self.user_preferences,
        }
        return current_state
            
    
    def get_user_id(self) -> str | None:
        return self.user_id        
    
    def add_top_products_to_userState(self, top_products: list[dict[str, Any]]) -> None:
        if self.user_id is None:
            print("User ID is not set. Cannot add top products to user state.")
        else:
            self.top_products.extend(top_products)
            self.check_duplication_in_top_products(self.top_products)
            print(f"Top products added to user state for user_id: {self.user_id} with products: {top_products}")
    
    def check_duplication_in_top_products(self, top_products: list[dict[str, Any]]) -> None:
            seen = set()
            unique_top_products = []
            for product in top_products:
                product_id = product.get('product_id')
                if product_id not in seen:
                    seen.add(product_id)
                    unique_top_products.append(product)
            self.top_products = unique_top_products
                  
   
      
        
    