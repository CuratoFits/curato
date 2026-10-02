from typing import Any
from app.service.embedding_db_service import EmbeddingDBService
from app.agents.userBehaviorAgent import UserBehaviorAgent
from app.state.userState import UserState
class VectorDBSearchAgent:
    def __init__(self,embeddingservice:EmbeddingDBService,userstate:UserState):
        self.embedding_db_service = embeddingservice
        self.userstate =userstate
        self.user_id = userstate.get_user_id()
        
    def contentBasedFilter(self,insights:dict[str,Any]) -> list[dict[str, Any]]:
        if self.user_id is None:
            print("User ID is not set. Cannot perform search.")
        else:
            vector=self.embedding_db_service.get_vector(insights)
            top_products = self.embedding_db_service.search_products(vector, top_k=100)   
            print(f"Search completed for user_id: {self.user_id}")
            product_ids = top_products['ids'][0]
            self.add_top_products_to_userState(product_ids)
    
    def add_top_products_to_userState(self, top_products:list[dict[str,Any]]):
        if self.user_id is None:
            print("User ID is not set. Cannot add top products to user state.")
        else:
            self.userstate.add_top_products_to_userState(top_products)
            print(f"Top products added to user state for user_id: {self.user_id}")    
            
            
    def collaborativeVectorFilter(self,vector: list[float], top_k: int) -> list[dict[str, Any]]:
        if self.user_id is None:
            print("User ID is not set. Cannot perform search.")
        else:
            print(f"Searching vector database for user_id: {self.user_id} with vector: {vector}")
            top_products = self.embedding_db_service.search_products(vector, top_k=top_k)   
            print(f"Search completed for user_id: {self.user_id} with vector: {vector}")
            product_ids = top_products['ids'][0]
            self.userstate.add_top_products_to_userState(product_ids)
            