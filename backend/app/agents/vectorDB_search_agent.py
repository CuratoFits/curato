from typing import Any

from app.service.embedding_db_service import EmbeddingDBService
from app.agents.userBehaviorAgent import UserBehaviorAgent
from app.state.userState import UserState
class VectorDBSearchAgent:
    def __init__(self):
        self.embedding_db_service = EmbeddingDBService()
        self.userstate = UserState()
        self.user_id = self.userstate.get_user_id()
        
    def searchVectorDB(self,text:dict[str,Any]) -> list[dict[str, Any]]:
        if self.user_id is None:
            print("User ID is not set. Cannot perform search.")
        else:
            text=text
            print(f"Searching vector database for user_id: {self.user_id} with text: {text}")
            top_products = self.embedding_db_service.search_embedding(text, top_k=100)   
            print(f"Search completed for user_id: {self.user_id} with text: {text}")
            return top_products
    
    def add_top_products_to_userState(self, top_products):
        if self.user_id is None:
            print("User ID is not set. Cannot add top products to user state.")
        else:
            self.userstate.add_top_products_to_userState(top_products)
            print(f"Top products added to user state for user_id: {self.user_id}")    
            
            
    def search_vectors(self,vector: list[float], top_k: int) -> list[dict[str, Any]]:
        if self.user_id is None:
            print("User ID is not set. Cannot perform search.")
        else:
            print(f"Searching vector database for user_id: {self.user_id} with vector: {vector}")
            top_products = self.embedding_db_service.search_embedding(vector, top_k=top_k)   
            print(f"Search completed for user_id: {self.user_id} with vector: {vector}")
            return top_products